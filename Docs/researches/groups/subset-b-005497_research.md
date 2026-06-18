# Research: subset-b-005497

Grouped research for USB gadget legacy drivers, shared helpers, and UDC controller files. Each section preserves the source path in the title and is wrapped for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/inode.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/inode.c

Purpose: implements GadgetFS, a pseudo filesystem that lets a userspace process drive a USB gadget controller through file descriptors. The mounted root contains an ep0 device file named after the selected UDC and later creates one file per non-control endpoint after the userspace driver writes device/configuration descriptors.

Important APIs, types, and functions: `struct dev_data` owns ep0 state, descriptor buffers, the `usb_gadget_driver`, queued `usb_gadgetfs_event` entries, and the mounted superblock link. `struct ep_data` owns a non-control endpoint file, endpoint descriptors, a preallocated `usb_request`, and its state. `gadgetfs_fill_super`, `gadgetfs_get_tree`, and `gadgetfs_kill_sb` implement the filesystem lifecycle. `dev_config` parses the userspace descriptor blob and registers `gadgetfs_driver`. `gadgetfs_bind`, `gadgetfs_unbind`, `gadgetfs_setup`, `gadgetfs_disconnect`, and `gadgetfs_suspend` integrate with the UDC core. Endpoint I/O is handled by `ep_read_iter`, `ep_write_iter`, `ep_config`, `ep_io`, `ep_ioctl`, and the AIO helpers `ep_aio`, `ep_aio_complete`, and `ep_aio_cancel`.

Control flow: mount allocates one `dev_data`, names the ep0 file from `usb_get_gadget_udc_name`, and waits for the ep0 file to be opened. The first write to ep0 must contain tag 0, full-speed config, optional high-speed config, and the device descriptor; successful parsing registers the gadget driver. Bind allocates ep0 request storage and creates endpoint files for every hardware endpoint. Reads from ep0 return connect, disconnect, suspend, or setup events; setup events move ep0 into `STATE_DEV_SETUP`, where subsequent reads/writes complete or stall the control transfer. Non-control endpoint files start `STATE_EP_DISABLED`, become `STATE_EP_READY` on open, accept a tag 1 endpoint descriptor write, then move to `STATE_EP_ENABLED` for normal read/write transfers.

State and persistence: all state is in kernel memory for the lifetime of the mount, ep0 fd, and endpoint fds. `dev->lock` protects device state and event queue fields, while each endpoint has a mutex plus device spinlock coordination for UDC references. `the_device` and `CHIP` are singleton globals guarded by `sb_mutex`, so only one GadgetFS mount/device is active. Module parameters `default_uid`, `default_gid`, and `default_perm` control file ownership/mode. No durable storage is written.

Dependencies and integration points: depends on VFS single-superblock helpers, `linux/usb/gadgetfs.h` UAPI events, the gadget UDC API, descriptor definitions from USB ch9, and delayed status semantics from composite support. Userspace must provide coherent descriptors and must service delegated setup requests promptly. UDC operations used include `usb_gadget_register_driver`, `usb_ep_queue`, `usb_ep_enable`, `usb_ep_set_halt`, `usb_ep_fifo_status`, `usb_ep_fifo_flush`, and optional gadget ioctl forwarding.

Risks: this is a userspace-facing kernel ABI with many race-sensitive state transitions. Descriptor validation is intentionally shallow and has FIXME notes around walking descriptor lengths and OTG descriptors. Concurrent ep0 readers can lose events. AIO cancellation/disconnect handling depends on careful lifetime management across workqueue copyback and `mm` use. Setup delegation must not timeout, and wrong-direction endpoint I/O intentionally halts endpoints. Unbind waits for `udc_usage`, so missing decrements would hang teardown.

Test signals: mount/unmount `gadgetfs`, open the `$CHIP` file once, write valid and invalid descriptor blobs, enumerate at full/high speed, exercise SET_CONFIGURATION and delegated class/vendor setup traffic, configure endpoint files and run bulk/interrupt/iso read/write, test nonblocking and AIO cancellation paths, issue FIFO ioctls, disconnect during active transfers, and verify no endpoint files or references remain after ep0 close/unmount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/mass_storage.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/mass_storage.c

Purpose: legacy `g_mass_storage` composite gadget wrapper for the mass-storage function. It supplies descriptors, module parameters, LUN setup, OTG descriptor handling, and composite registration while leaving SCSI/Bulk-Only transport behavior to `f_mass_storage`.

Important APIs, types, and functions: `msg_device_desc` declares the USB device descriptor; `mod_data` and `FSG_MODULE_PARAMETERS` expose file-backed storage options; `fi_msg` and `f_msg` hold the function instance/function. `msg_bind` obtains the `"mass_storage"` function instance, converts module parameters into `struct fsg_config`, configures common storage buffers, cdev, sysfs, LUNs, inquiry strings, string IDs, and OTG descriptors. `msg_do_config` adds the mass-storage function to the single configuration. `msg_unbind` releases the function, instance, and OTG descriptor.

Control flow: module registration through `module_usb_composite_driver` calls `msg_bind` when a UDC binds. Bind prepares mass-storage common state before calling `usb_add_config`. When the configuration is selected, `msg_do_config` gets a live function from the instance and adds it. Error paths unwind LUNs, buffers, descriptors, and function instances in reverse order.

State and persistence: global static descriptor and function pointers exist for the module lifetime. Runtime LUN/file-backed state lives in the mass-storage common object and is configured from module parameters. No state is persisted by this wrapper.

Dependencies and integration points: depends on libcomposite and `f_mass_storage.h`. The wrapper relies on `fsg_common_set_num_buffers`, `fsg_common_set_cdev`, `fsg_common_create_luns`, `fsg_common_set_sysfs`, and `usb_composite_overwrite_options`. It uses NetChip vendor/product defaults and requires a serial number (`needs_serial = 1`).

Risks: all meaningful media and SCSI risks are in the function core, but this wrapper can leak or double-release if bind partially succeeds and unwind ordering is wrong. Incorrect module parameters can prevent LUN creation. OTG descriptor allocation is global and must be freed on unbind/failure.

Test signals: load with valid backing-file parameters, enumerate `g_mass_storage`, verify descriptors/string overrides, mount/read/write from a host, test missing/invalid LUN parameters, run disconnect/reconnect during I/O, and unload while ensuring LUNs, buffers, and function references are released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/mass_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/multi.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/multi.c

Purpose: legacy `g_multi` composite gadget combining serial ACM, Ethernet (`ecm` and/or `rndis` depending on Kconfig), and mass-storage functions in one or two configurations.

Important APIs, types, and functions: `device_desc`, `strings_dev`, `fsg_mod_data`, and Ethernet module parameters define the exported USB personality. `multi_bind` obtains and configures function instances for ECM, RNDIS, ACM, and mass storage. `rndis_do_config` and `cdc_do_config` add functions in per-configuration order. `rndis_config_register` and `cdc_config_register` register configurations conditionally. `multi_unbind` releases every function/function-instance and frees OTG descriptors.

Control flow: bind first validates ECM support, sets Ethernet queue multiplier and MAC addresses, optionally shares one netdev between ECM and RNDIS, then initializes ACM and mass storage. It allocates string IDs, optional OTG descriptor, and registers RNDIS and/or CDC configurations. At configuration bind time functions are acquired and added in network, serial, storage order. Error labels unwind each completed stage.

State and persistence: module globals track function instances and per-configuration function objects. Mass-storage LUN state is created during bind from module parameters; Ethernet addresses come from module parameters or generated defaults in `u_ether`. No persistent data is stored here.

Dependencies and integration points: depends on libcomposite, `u_serial`, `u_ecm`, `u_rndis`/`rndis` when enabled, `u_ether`, and `f_mass_storage`. It integrates with the Linux network stack through gether helpers and with storage through fsg common helpers. `CONFIG_USB_G_MULTI_CDC` and `CONFIG_USB_G_MULTI_RNDIS` shape the descriptor surface.

Risks: mixed function lifetimes are the main risk. The dual ECM/RNDIS path borrows a net interface, so registration and teardown ordering must be exact. Some hosts are sensitive to function ordering and IAD/device class choices. Partial failure after adding one configuration can leave function references unless all unwind labels remain correct.

Test signals: build all Kconfig variants, enumerate with RNDIS-only, CDC-only, and dual configurations, verify MAC address module parameters, run network traffic and serial console while copying to mass storage, switch configurations on the host, test bind failure injection around LUN and OTG allocation, and unload after active network/storage use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/ncm.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/ncm.c

Purpose: legacy `g_ncm` composite wrapper exporting one CDC NCM Ethernet function.

Important APIs, types, and functions: `device_desc` sets CDC communication class defaults, `strings_dev` supplies dynamic strings, `f_ncm_inst` and `f_ncm` track the NCM function. `gncm_bind` gets the `"ncm"` function instance, programs gether options such as `qmult`, host MAC, and device MAC, assigns string IDs, allocates OTG descriptors, and registers `ncm_config_driver`. `ncm_do_config` gets the function and adds it to the configuration. `gncm_unbind` releases resources.

Control flow: composite bind prepares NCM network options before any configuration is added. When the host selects the single configuration, the NCM function is materialized and attached. OTG-capable gadgets get wakeup attributes and descriptor pointers.

State and persistence: runtime state is global to the module and in the gether network object owned by `struct f_ncm_opts`. MAC/module options are in memory only. No durable state is maintained.

Dependencies and integration points: depends on libcomposite, `u_ether`, and `u_ncm`. It creates a Linux network interface through gether internals and relies on the UDC/composite core for descriptor completion and string override handling.

Risks: failures after function-instance acquisition must release the instance and OTG descriptor. MAC address handling affects host networking identity. Some UDCs or hosts may be sensitive to NCM descriptor correctness and max speed.

Test signals: enumerate as `g_ncm`, inspect CDC NCM descriptors, verify network interface creation, pass traffic in both directions, test configured MAC parameters, exercise disconnect/reconnect, and unload while traffic is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/ncm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/nokia.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/nokia.c

Purpose: legacy Nokia N900 PC-Suite composite gadget exposing two configurations with ACM, ECM, mass storage, and optional Phonet/OBEX functions.

Important APIs, types, and functions: `device_desc`, `nokia_config_500ma_driver`, and `nokia_config_100ma_driver` define the two advertised configurations. `fsg_mod_data` configures two removable non-stalling LUNs. `nokia_bind` allocates string IDs, checks alternate setting support, obtains function instances, prepares mass-storage common state, and registers both configurations. `nokia_bind_config` materializes optional and mandatory functions and records per-configuration function pointers for unbind. `nokia_unbind` releases all functions and instances.

Control flow: bind first handles strings and hardware capability, then optional Phonet and OBEX instances are best-effort while ACM, ECM, and mass storage are required. Each configuration receives its own function objects from shared instances. Optional functions are added first if available, followed by ACM, ECM, and storage. Failure paths remove any functions already added and drop references.

State and persistence: static globals track function instances and per-config function objects. Storage LUNs and inquiry strings are prepared at bind time. Configurations differ by bus/self-powered attributes and max power values. No persistent state is written.

Dependencies and integration points: depends on libcomposite, `u_serial`, `u_ether`, `u_phonet`, `u_ecm`, and `f_mass_storage`. It integrates with hosts expecting Nokia vendor/product IDs and PC-Suite style interface composition.

Risks: optional function handling creates many `IS_ERR_OR_NULL` paths, and errors can easily cause missing puts or stale per-config pointers. The driver requires `gadget_is_altset_supported`, limiting UDC compatibility. Reusing old Nokia IDs and fixed composition can confuse modern hosts if descriptors change.

Test signals: build with and without Phonet/OBEX support, enumerate both configurations, verify 500 mA and 100 mA attributes, test ACM, ECM, and both storage LUNs, switch configurations repeatedly, inject optional function acquisition failure, and unload after both configurations have been bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/nokia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/printer.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/printer.c

Purpose: legacy `g_printer` composite wrapper around the printer function, exposing a USB printer-class gadget with configurable serial, PNP string, and endpoint request queue length.

Important APIs, types, and functions: module parameters `iSerialNum`, `iPNPstring`, and `qlen` feed composite overrides and `f_printer_opts`. `printer_bind` gets the `"printer"` function instance, sets minor and queue length, installs the PNP string, assigns string IDs, allocates optional OTG descriptors, and registers `printer_cfg_driver`. `printer_do_config` resets endpoint autoconfig, marks self-powered, applies OTG descriptors, gets `f_printer`, and adds it. `printer_unbind` releases function resources.

Control flow: bind prepares function options before registering the configuration. During config bind, the printer function is added to the single configuration. On error, function instance and OTG descriptor ownership are unwound; allocated PNP string ownership is delegated to printer function cleanup as noted in the code.

State and persistence: global descriptor strings and function pointers persist while the module is loaded. Runtime printer buffering and device node behavior live in `u_printer`/`f_printer`. No durable state is written.

Dependencies and integration points: depends on libcomposite, USB printer UAPI definitions, and `u_printer.h`. It exposes a printer gadget that typically creates a gadget-side printer character device through the function implementation.

Risks: `qlen` affects memory use and throughput. PNP string allocation/ownership relies on lower-level cleanup. Endpoint autoconfig reset is required before adding the function, and missing it can produce endpoint conflicts. Host printer-class behavior is descriptor-string sensitive.

Test signals: enumerate with default and custom PNP strings, inspect printer class descriptors, verify gadget-side printer device I/O, test large queue lengths, disconnect during active transfers, and unload while confirming function and OTG descriptor release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/printer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/raw_gadget.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/raw_gadget.c

Purpose: implements the Raw Gadget miscdevice ABI (`/dev/raw-gadget`) that lets userspace emulate arbitrary USB devices by directly driving control requests, endpoint enablement, and endpoint I/O through ioctls.

Important APIs, types, and functions: `struct raw_dev` owns the UDC name, `usb_gadget_driver`, EP0 request, endpoint table, event queue, and state machine. `struct raw_event_queue` is a bounded semaphore-backed queue for connect/control/disconnect/suspend/resume/reset events. `struct raw_ep` stores endpoint state, descriptor address, request, and in-flight flags. File operations are `raw_open`, `raw_ioctl`, and `raw_release`. Important ioctls include `raw_ioctl_init`, `raw_ioctl_run`, `raw_ioctl_event_fetch`, `raw_ioctl_ep0_read/write/stall`, `raw_ioctl_ep_enable/disable`, `raw_ioctl_ep_read/write`, halt/wedge controls, `raw_ioctl_configure`, `raw_ioctl_vbus_draw`, and `raw_ioctl_eps_info`.

Control flow: open allocates one independent `raw_dev`. `USB_RAW_IOCTL_INIT` copies UDC names and requested speed, assigns a unique driver name, and fills a gadget driver with callbacks. `USB_RAW_IOCTL_RUN` registers that driver; bind verifies the requested UDC, allocates the EP0 request, snapshots available endpoints, and queues a connect event. Setup, disconnect, suspend, resume, and reset callbacks enqueue events for userspace. Userspace fetches events, responds to control transfers through EP0 ioctls, enables endpoints by descriptor matching, performs synchronous endpoint I/O, and finally closes the fd to unregister and free resources.

State and persistence: state is per open fd and reference-counted with `kref` across file and gadget bind lifetimes. `dev->lock` protects device/endpoint state. Endpoint I/O allows one in-flight request per endpoint. Event queue depth is fixed at 16; overflow marks the device failed. Global `driver_id_numbers` only allocates unique transient names. No persistent state exists.

Dependencies and integration points: depends on miscdevice, Raw Gadget UAPI, the UDC gadget-driver API, endpoint descriptor matching, and `usb_gadget_set_state`/`usb_gadget_vbus_draw`. It is commonly used by fuzzers and USB emulators because userspace controls descriptors and transfer timing.

Risks: this is intentionally powerful userspace control over USB device behavior, so validation boundaries are critical. The code guards max I/O length, endpoint number, flags, zero maxpacket descriptors, wrong direction, duplicate URBs, and invalid state transitions. Event queue overflow forces `STATE_DEV_FAILED`. Completion waits can be interrupted and then dequeue requests, so status translation and locking must be correct. `dev_free` disables endpoints and frees descriptors, making lifetime bugs severe.

Test signals: run Raw Gadget UAPI tests, initialize against a named UDC, fetch connect/control events, emulate enumeration, test zero-length delayed-status control transfers, enable bulk/interrupt/iso endpoints, perform IN/OUT I/O, verify halt/wedge/clear behavior, query endpoint info, force disconnect during pending I/O, overflow events, and close during registered operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/raw_gadget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/serial.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/serial.c

Purpose: legacy `g_serial` composite gadget exposing one or more USB serial ports as CDC ACM, CDC OBEX, or vendor-specific generic serial functions.

Important APIs, types, and functions: module parameters `use_acm`, `use_obex`, `n_ports`, and dynamic `enable` choose function type, port count, and registration state. `serial_register_ports` adds the configuration and loops over ports, getting a function instance/function for `acm`, `obex`, or `gser`. `gs_bind` assigns strings, optional OTG descriptor, and registers the selected ports. `switch_gserial_enable`, `enable_set`, `gserial_init`, and `gserial_cleanup` implement runtime composite probe/unregister toggling.

Control flow: module init chooses descriptor class, product ID, configuration label/value, and string text based on `use_acm`/`use_obex`. If `enable` is true, it probes the composite driver. Bind creates string IDs and adds N serial functions to the one configuration. Runtime writes to the `enable` module parameter can register or unregister the composite driver after init.

State and persistence: static arrays `fi_serial` and `f_serial` hold per-port references up to `MAX_U_SERIAL_PORTS`. Module parameters persist only while the module is loaded. TTY buffering and port state live in the serial function implementation.

Dependencies and integration points: depends on libcomposite, `u_serial`, Linux TTY support, and the ACM/OBEX/generic serial USB function providers. It exposes host-visible serial ports and gadget-side TTY endpoints through lower layers.

Risks: `n_ports` must stay within the function framework limit; this file does not visibly clamp before indexing the static arrays, so validation is expected elsewhere or by parameter discipline. Runtime enable toggling can race conceptually with active host sessions, relying on composite unregister to quiesce. Function acquisition failures must unwind every previously added port.

Test signals: load with ACM, OBEX, and generic modes; vary `n_ports`; verify descriptors/product IDs; open gadget TTYs and host serial devices; toggle `enable` at runtime; disconnect during serial traffic; and unload while all ports are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/tcm_usb_gadget.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/tcm_usb_gadget.c

Purpose: legacy `g_target` USB target gadget wrapper connecting the USB TCM/UAS function with the Linux target fabric attachment model.

Important APIs, types, and functions: `usbg_device_desc`, `usbg_us_strings`, and `usbg_config_driver` define the composite descriptor surface. `fi_tcm` and `f_tcm` track the target function. `usb_target_gadget_init` gets the `"tcm"` function instance, configures dependency callbacks in `struct f_tcm_opts`, names the instance `tcm-legacy`, and defers actual composite registration until the target fabric calls `usbg_attach`. `usb_target_bind` assigns string IDs and adds the TCM function via `tcm_do_config`. `usbg_detach` unregisters the composite driver.

Control flow: module init does not immediately bind a UDC; it prepares callbacks so the TCM fabric can attach/detach the USB gadget. Attach probes the composite driver, bind assigns strings and registers a single self-powered configuration, and config bind adds the TCM function. Detach unregisters the composite driver. Exit releases the function instance.

State and persistence: dependency flags and callbacks live in the TCM function options under `dep_lock`. Function object `f_tcm` is released on composite unbind. Storage target state is owned by target-core and the TCM function, not this wrapper.

Dependencies and integration points: depends on libcomposite, `u_tcm`, target core/fabric headers, SCSI constants, and USB storage/UAS protocol support. It bridges target-core configuration to USB gadget enumeration.

Risks: callback registration under `dep_lock` must match target-core expectations. The wrapper only releases `f_tcm` in unbind and `fi_tcm` in module exit, so attach/detach ordering must remain coherent. Target configuration errors can prevent any UDC registration.

Test signals: configure a USB target fabric endpoint, trigger attach, enumerate as `g_target`, verify UAS/BOT behavior from a host, detach and reattach target configuration, unload after detach, and test error handling when the TCM function instance is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/tcm_usb_gadget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/webcam.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/webcam.c

Purpose: legacy `g_webcam` UVC composite gadget with built-in video-control and streaming descriptors for YUY2 and MJPEG at 360p and 720p.

Important APIs, types, and functions: module parameters `streaming_interval`, `streaming_maxpacket`, and `streaming_maxburst` configure the isochronous streaming endpoint. Static UVC descriptors define camera terminal, processing unit, output terminal, input header, uncompressed YUY2 formats, MJPEG formats, frame intervals, and color matching. `webcam_bind` gets the `"uvc"` function instance, fills `struct f_uvc_opts`, builds configfs-style linked lists of formats/frames/header, assigns string IDs, and registers `webcam_config_driver`. `webcam_config_bind` adds the UVC function; `webcam_unbind` releases it.

Control flow: bind wires static descriptor arrays and runtime linked-list metadata into UVC function options before adding the single configuration. The UVC function then owns video request handling and streaming behavior. Composite options may override descriptor strings and IDs.

State and persistence: descriptor objects are static. Linked lists are initialized at bind time using global nodes, so the module assumes one active binding. UVC runtime state, video device behavior, and streaming queues live in `u_uvc`. No persistent state is stored.

Dependencies and integration points: depends on libcomposite, USB video class descriptors, `u_uvc`, and `uvc_configfs` data structures. It integrates with V4L2/UVC gadget userspace through the UVC function implementation.

Risks: static descriptor graphs must remain internally consistent in frame counts, indexes, intervals, and header references. Module parameter bounds are described but not strongly validated here, so invalid endpoint settings may fail later or produce bad descriptors. Re-initializing global list nodes would be risky if multiple bindings were ever allowed.

Test signals: enumerate at full/high/super speed, inspect UVC descriptors with `lsusb -v`, open the host camera, stream YUY2 and MJPEG modes at both advertised resolutions, vary streaming endpoint parameters, disconnect during streaming, and unload while ensuring UVC function references are released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/webcam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/zero.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/zero.c

Purpose: `g_zero`, the development/test gadget with source/sink and loopback configurations for exercising UDC, composite, endpoint, suspend/resume, and remote wakeup behavior.

Important APIs, types, and functions: `gzero_options` stores bulk, isochronous, queue-depth, and pattern parameters. `zero_bind` gets `SourceSink` and `Loopback` function instances, copies module options into their option structs, assigns strings, configures OTG/autoresume behavior, adds both configurations, and attaches the functions. `ss_config_setup` forwards source/sink vendor control requests. `zero_suspend`, `zero_resume`, and `zero_autoresume` implement timed remote wakeup testing. `zero_unbind` deletes the timer and releases resources.

Control flow: bind creates two configurations in an order controlled by `loopdefault`, adds source/sink and loopback functions after endpoint autoconfig resets, and enables wakeup attributes when autoresume or OTG requires them. Suspend arms a timer; the timer calls `usb_func_wakeup` on superspeed-capable function paths or `usb_gadget_wakeup` otherwise. Resume deletes the timer.

State and persistence: module parameters define transient runtime behavior. `autoresume_timer`, `autoresume_cdev`, and `autoresume_step_ms` maintain wakeup-test state while bound. No durable state exists.

Dependencies and integration points: depends on libcomposite and `g_zero.h` function implementations for SourceSink and Loopback. It is designed to pair with host-side `usbtest` and descriptor/transfer test tools.

Risks: because this driver is used as a test oracle, descriptor/configuration ordering and wakeup behavior must stay stable. Timer lifetime must be synchronized on unbind. Parameter combinations for isochronous maxpacket/mult/burst and queue lengths can expose UDC limitations.

Test signals: run host `usbtest`, enumerate both configurations with `loopdefault` true/false, exercise source/sink control requests 0x5b/0x5c, run loopback bulk tests, vary pattern and buffer lengths, test isochronous options, suspend/resume with autoresume and max-autoresume stepping, and unload during idle and after suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/zero.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/u_f.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/u_f.c

Purpose: shared USB gadget function utility implementing request allocation with endpoint-aware buffer sizing.

Important APIs, types, and functions: `alloc_ep_req(struct usb_ep *ep, size_t len)` allocates a `usb_request` with `usb_ep_alloc_request`, sets `req->length`, allocates `req->buf`, and exports the helper with `EXPORT_SYMBOL_GPL`.

Control flow: the helper allocates the request in atomic context. For OUT endpoints, it aligns requested length with `usb_ep_align(ep, len)` to satisfy controller DMA/cache constraints; for IN endpoints it keeps the requested length. If buffer allocation fails, it frees the request and returns NULL.

State and persistence: no persistent state. The caller owns the returned request and buffer and must free both through the matching endpoint/function cleanup path.

Dependencies and integration points: depends on USB endpoint descriptors, `linux/usb/func_utils.h`, and endpoint allocator/free APIs. Function drivers use it to standardize request and buffer allocation.

Risks: callers must only pass endpoints with valid descriptors because direction is read from `ep->desc`. GFP_ATOMIC can fail under memory pressure. The helper allocates but does not initialize completion callbacks or list nodes.

Test signals: call from IN and OUT endpoints and verify lengths, alignment, NULL handling on allocation failure, and correct cleanup through `usb_ep_free_request` plus `kfree(req->buf)` in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/u_f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/u_os_desc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/u_os_desc.h

Purpose: inline helper header for building Microsoft OS extended property descriptors in little-endian layout.

Important APIs, types, and functions: constants define offsets and property data types. Pointer helpers return locations for size, type, name length, name, data length, and data. Writer helpers include `usb_ext_prop_put_size`, `usb_ext_prop_put_type`, `usb_ext_prop_put_name`, `usb_ext_prop_put_binary`, and `usb_ext_prop_put_unicode`.

Control flow: callers pass a preallocated descriptor buffer. The helpers write unaligned little-endian fields, convert UTF-8 strings to UTF-16LE for property names/data, add UTF-16 NUL terminators, and return either written lengths or conversion errors.

State and persistence: no state. The buffer and bounds are entirely caller-owned.

Dependencies and integration points: depends on `linux/unaligned.h` and `linux/nls.h`. Used by gadget configfs/function code that advertises OS descriptors to Windows hosts.

Risks: helpers do not validate total buffer capacity, so caller-side size computation must be correct. `usb_ext_prop_put_unicode` uses `data_len >> 1` as the source character count for UTF-8 conversion, which assumes caller passes compatible sizing. Offsets depend on the OS descriptor format and must not drift.

Test signals: build descriptors with ASCII and multibyte UTF-8 property names/data, verify little-endian fields and terminators, test binary property placement, run with undersized buffers under KASAN in callers, and validate enumeration on Windows OS descriptor consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/u_os_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/Kconfig

Purpose: Kconfig menu defining USB peripheral controller driver options under "USB Peripheral Controller".

Important APIs, types, and functions: this is declarative Kconfig. It defines controller symbols such as `USB_AT91`, `USB_LPC32XX`, `USB_ATMEL_USBA`, `USB_FSL_USB2`, `USB_SNP_CORE`, `USB_AMD5536UDC`, `USB_NET2280`, `USB_ASPEED_UDC`, and `USB_DUMMY_HCD`, and sources submenus for `bdc`, `aspeed-vhub`, and `cdns2`.

Control flow: integrated SoC controllers are listed before licensed/discrete/PCI controllers, with dummy HCD last. Dependencies restrict symbols to matching architectures, buses, DMA, OF, EXTCON, PHY, or USB PCI support. Some symbols select shared support, such as `USB_AMD5536UDC` selecting `USB_SNP_CORE`.

State and persistence: selected Kconfig symbols become build configuration state, not runtime state. Tristate options control built-in versus module builds and indirectly force gadget drivers to compatible linkage.

Dependencies and integration points: integrates with the kernel configuration system and the UDC Makefile. It is the entry point for enabling platform-specific UDC drivers that libcomposite and legacy gadget drivers bind to.

Risks: incorrect dependencies can expose drivers on unsupported builds or hide valid compile-test coverage. `select` relationships can force shared core code unexpectedly. Help text and module names must stay synchronized with Makefile object names.

Test signals: run `make olddefconfig`, `allmodconfig`, and architecture-specific configs; verify each selected symbol builds its Makefile object; check compile-test dependencies; and confirm dummy HCD remains last for default selection behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/Makefile

Purpose: builds the UDC core and selected USB peripheral controller drivers from Kconfig symbols.

Important APIs, types, and functions: `udc-core-y := core.o trace.o` builds common UDC support; `CFLAGS_trace.o` points trace generation at the source directory. `obj-$(CONFIG_...)` lines map each controller symbol to its object or subdirectory. Multi-object aliases include `fsl_usb2_udc-y := fsl_udc_core.o`.

Control flow: kbuild includes `udc-core.o` whenever `CONFIG_USB_GADGET` is enabled, then conditionally descends into controller objects such as `dummy_hcd.o`, `net2280.o`, `amd5536udc_pci.o`, `aspeed-vhub/`, `bdc/`, and `cdns2/`.

State and persistence: no runtime state. Build outputs depend on Kconfig values.

Dependencies and integration points: ties `drivers/usb/gadget/udc/Kconfig` symbols to compiled objects and subdirectories. The trace CFLAGS line supports local trace header inclusion.

Risks: symbol/object drift causes selected drivers not to build. Subdirectory entries require their own Makefiles. Missing shared object mappings can break link when Kconfig selects a core symbol.

Test signals: build each UDC symbol as module and built-in, run `make W=1 drivers/usb/gadget/udc/`, verify trace compilation, and compare Kconfig symbols against Makefile entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/amd5536udc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/amd5536udc.h

Purpose: shared hardware definitions and core data structures for the AMD5536/Synopsys USB 2.0 device controller implementation.

Important APIs, types, and functions: register offsets and bit masks cover global CSRs, device configuration/control/status/interrupt registers, endpoint registers, FIFO sizes, setup command words, and DMA descriptor status fields. `struct udc_regs`, `struct udc_ep_regs`, `struct udc_stp_dma`, and `struct udc_data_dma` model hardware layout. `struct udc_request`, `struct udc_ep`, and `struct udc` are the software request, endpoint, and device objects. It declares core functions such as `udc_irq`, `udc_probe`, `udc_remove`, `init_dma_pools`, `free_dma_pools`, and `udc_basic_init`. Module parameters `use_dma`, `use_dma_ppb`, `use_dma_ppb_du`, and `use_fullspeed` tune operation.

Control flow: this header is consumed by PCI/platform glue and core controller code. Register macros feed initialization, interrupt handling, endpoint enablement, DMA descriptor construction, and setup packet decoding. Data structures hold queues, DMA pools, endpoint registers, FIFO pointers, UDC state, extcon/PHY support, and gadget core linkage.

State and persistence: no executable state except static module-parameter variables when included into implementation units. Runtime state lives in `struct udc`, protected by `dev->lock`, and includes current configuration/interface/altsetting, DMA pools, connection flags, and endpoint queues.

Dependencies and integration points: depends on USB ch9, gadget core, extcon, PHY, DMA pool usage, and PCI/platform glue. It also connects to Synopsys core support selected through Kconfig.

Risks: packed/aligned structures must match hardware DMA/register layout exactly. Bitfield macros and constants are widely reused, so a wrong mask or offset corrupts hardware programming. Static module parameters in a header are unusual and require careful inclusion expectations. DMA alignment and 32-bit address constraints are highlighted by the PCI driver comments.

Test signals: compile all users, boot/probe hardware in DMA and PIO modes, enumerate at full/high speed, exercise endpoint interrupts and setup commands, run with `use_fullspeed`, validate DMA descriptor ownership transitions, and run sparse/endianness checks over register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/amd5536udc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/amd5536udc_pci.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/amd5536udc_pci.c

Purpose: PCI bus glue for the AMD5536 UDC, mapping hardware resources and invoking the shared UDC core.

Important APIs, types, and functions: global `udc` enforces a single controller instance. `udc_pci_probe` enables the PCI device, requests BAR0 memory, maps registers, requests IRQ, initializes register/FIFO pointers in `struct udc`, sets bus mastering/MWI, initializes DMA pools when enabled, and calls `udc_probe`. `udc_pci_remove` unregisters the gadget UDC, frees DMA pools, resets the controller, releases IRQ/mapping/memory/PCI state, and calls `udc_remove`. `pci_id` matches AMD vendor device `0x2096` with USB device class.

Control flow: PCI probe performs allocation and hardware resource acquisition in stages with labeled unwind. If core probe succeeds, the global `udc` pointer is set. Remove deletes the gadget UDC before requiring no gadget driver to remain, then performs hardware and memory teardown.

State and persistence: all runtime state is in one allocated `struct udc` and the global pointer. PCI driver data points to the device object. No durable state exists.

Dependencies and integration points: depends on PCI, MMIO, IRQ, DMA pools, and the AMD5536 core declarations from `amd5536udc.h`. It registers through `module_pci_driver`, exposing a UDC to the gadget framework after `udc_probe`.

Risks: the file assumes one UDC only. Remove uses global `udc->gadget` rather than local `dev->gadget`, which is safe only if the singleton invariant holds. Resource unwind must mirror acquisition. DMA mode can be disabled through module parameters when alignment-sensitive gadget functions fail.

Test signals: probe on matching PCI hardware, verify BAR mapping and IRQ handling, bind a gadget, enumerate and transfer data, unload with and without a gadget bound, test probe failure injection at each resource stage, and run both `use_dma=1` and `use_dma=0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/amd5536udc_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/Kconfig

Purpose: Kconfig entry for the Aspeed virtual hub USB gadget controller driver.

Important APIs, types, and functions: defines `USB_ASPEED_VHUB` as a tristate "Aspeed vHub UDC driver", depending on `ARCH_ASPEED || COMPILE_TEST` and `USB_LIBCOMPOSITE`.

Control flow: when selected, the parent UDC Makefile descends into `aspeed-vhub/` and builds the virtual hub controller module/object.

State and persistence: selected Kconfig state controls build inclusion only.

Dependencies and integration points: integrates with Aspeed SoC device-tree platform support and libcomposite. The help text documents AST2400, AST2500, and AST2600 vHub USB2.0 functionality.

Risks: the dependency on `USB_LIBCOMPOSITE` means builds without libcomposite cannot enable this UDC, which is appropriate because it registers multiple gadget UDCs. Help text may need updates as newer compatibles such as AST2700 are supported in code.

Test signals: select as built-in and module on ARCH_ASPEED and COMPILE_TEST builds, verify Makefile object inclusion, and confirm device-tree compatible tables probe the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/Makefile

Purpose: kbuild recipe for the Aspeed vHub UDC driver.

Important APIs, types, and functions: maps `CONFIG_USB_ASPEED_VHUB` to `aspeed-vhub.o` and composes it from `core.o`, `ep0.o`, `epn.o`, `dev.o`, and `hub.o`.

Control flow: when the Kconfig symbol is enabled, kbuild compiles and links all five implementation objects into one driver.

State and persistence: build-only file with no runtime state.

Dependencies and integration points: must stay synchronized with declarations in `vhub.h` and calls between core, endpoint-zero, generic endpoint, device, and hub emulation files.

Risks: omitting one component breaks unresolved symbols or runtime functionality. Adding new implementation files requires this list to change.

Test signals: build as module and built-in, ensure all five objects link, and run modpost to catch missing exports or unresolved internal calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/core.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/core.c

Purpose: top-level platform driver and interrupt/hardware initialization for the Aspeed vHub UDC, a controller that emulates a USB hub with multiple downstream gadget ports.

Important APIs, types, and functions: `ast_vhub_done`, `ast_vhub_nuke`, `ast_vhub_alloc_request`, and `ast_vhub_free_request` provide shared request lifecycle helpers. `ast_vhub_irq` dispatches endpoint-pool ACKs, per-device interrupts, hub EP0 events, and bus resume/suspend/reset. `ast_vhub_init_hw` programs PHY/reset, descriptor-ring mode, endpoint interrupts, EP0 DMA, upstream pullup, and interrupt enables. `ast_vhub_probe` parses device-tree sizing, maps registers, enables clock/reset, requests IRQ, sets DMA mask, allocates coherent EP0 buffers, initializes root hub EP0, ports, hub emulation, and hardware. `ast_vhub_remove` tears all of it down.

Control flow: platform probe allocates `struct ast_vhub`, sizes port and generic endpoint arrays from DT or defaults, prepares hardware resources, installs the IRQ handler, allocates one coherent EP0 buffer per port plus one for the virtual hub, initializes children, and finally connects upstream. IRQ handling runs under `vhub->lock`, acknowledges interrupt sources, and delegates to `epn`, `dev`, `ep0`, and `hub` helpers.

State and persistence: runtime state lives in `struct ast_vhub`, including register base, clock/reset, IRQ, port array, generic endpoint pool, coherent EP0 buffers, speed/USB1 forcing, and spinlock. No durable state exists.

Dependencies and integration points: depends on platform/OF, clocks, reset control, DMA mapping, libcomposite/gadget UDC APIs, and internal `vhub.h` helpers from `hub.c`, `dev.c`, `ep0.c`, and `epn.c`. Device-tree compatibles choose 32-bit or 64-bit DMA masks.

Risks: interrupt dispatch and request completion deliberately drop/reacquire the spinlock around gadget callbacks. Teardown must prevent stale IRQs by checking `ep0_bufs` and masking hardware. Descriptor count assumptions are compile-time checked. Register accessibility during suspend influences the decision not to stop logic clock.

Test signals: probe on AST2400/2500/2600/2700 compatibles, vary DT port/endpoint counts, bind multiple gadget drivers to ports, enumerate through the virtual hub, exercise endpoint traffic, suspend/resume/reset bus events, remove the platform device, and run with DMA API debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/dev.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/dev.c

Purpose: manages each downstream vHub port as an independent `usb_gadget` UDC.

Important APIs, types, and functions: `ast_vhub_init_dev` creates a port device, initializes EP0, allocates per-port endpoint pointer array, populates `usb_gadget`, and calls `usb_add_gadget_udc`. `ast_vhub_del_dev` unregisters it. `ast_vhub_dev_irq`, `ast_vhub_dev_enable`, and `ast_vhub_dev_disable` handle per-port hardware interrupts and enable state. `ast_vhub_std_dev_request` handles standard device/endpoint requests before delegating to the gadget driver. UDC ops include `ast_vhub_udc_start`, `ast_vhub_udc_stop`, `ast_vhub_udc_pullup`, `ast_vhub_udc_wakeup`, `ast_vhub_udc_get_frame`, and `ast_vhub_udc_match_ep`.

Control flow: init registers each port as a separate UDC under a unique child device. A gadget driver start only stores the driver and self-powered flag; the virtual hub later enables the port on reset/connect. Standard requests handle address, status, remote wakeup, test mode, and endpoint halt state; unknown requests return `std_req_driver` for EP0 forwarding. Reset either enables a disabled port or calls `usb_gadget_udc_reset`, disables hardware, and re-enables it. Endpoint matching first reuses existing endpoints, then allocates a generic endpoint from the shared pool with a unique address.

State and persistence: `struct ast_vhub_dev` tracks driver, enabled/registered flags, wakeup enable, speed, per-port EP0, and endpoint mappings. State is protected by `vhub->lock`. No persistent data exists.

Dependencies and integration points: integrates with gadget UDC core, hub emulation (`ast_vhub_device_connect`, wake functions), EP0 handling, and generic endpoint allocation from `epn.c`. It uses USB standard request constants and HCD-visible frame register state.

Risks: endpoint allocation must avoid overlapping IN/OUT numbers because hardware cannot support generic duplicate addresses. Standard request handling must not incorrectly stall class/vendor traffic. Pullup disables hardware and nukes requests, so active gadget drivers must tolerate shutdown callbacks. Lock dropping around gadget driver callbacks must preserve object lifetime.

Test signals: register multiple gadgets on vHub ports, connect/disconnect via pullup, issue standard GET_STATUS/SET_ADDRESS/FEATURE requests, allocate endpoints of all supported types, test endpoint halt clear/set, suspend/resume callbacks, remote wakeup enable and trigger, reset during active transfers, and unregister ports during driver removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/ep0.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/ep0.c

Purpose: endpoint-zero control transfer engine for both the virtual hub itself and each downstream virtual gadget device.

Important APIs, types, and functions: `ast_vhub_init_ep0` initializes EP0 objects and maps their control/status, setup, buffer, and DMA addresses. `ast_vhub_ep0_handle_setup` reads setup packets, routes standard/class hub requests or standard device requests, forwards driver-owned requests to gadget `setup`, and stalls or completes as needed. `ast_vhub_reply` and `__ast_vhub_simple_reply` send internal replies. `ast_vhub_ep0_handle_ack`, `ast_vhub_ep0_do_send`, `ast_vhub_ep0_do_receive`, and `ast_vhub_ep0_rx_prime` implement data/status phase progression. EP ops `ast_vhub_ep0_queue` and `ast_vhub_ep0_dequeue` connect gadget requests to the EP0 state machine. `ast_vhub_reset_ep0` nukes queued work and returns to token state.

Control flow: a SETUP IRQ copies the setup packet, recovers from unexpected states by nuking queued requests, sets data direction, and dispatches to hub/device standard handlers or the gadget driver. Internal replies queue through the same EP0 ops after dropping the lock. IN transfers send maxpacket-sized chunks from request buffers or the EP buffer; OUT transfers prime RX, copy received data into the request, and complete on short packet or expected length. ACK IRQs advance data or status phases and return to token state unless a stall is needed.

State and persistence: EP0 state is in `ep->ep0.state`, `dir_in`, internal request object, queue, and per-EP coherent buffer. Only one EP0 request is allowed at a time. State is protected by `vhub->lock`; completion can drop the lock to call gadget callbacks. No persistent data exists.

Dependencies and integration points: depends on internal hub request handlers, device standard request handler, gadget driver `setup`, hardware EP0 control/status registers, DMA buffer workaround helper, and shared request completion from `core.c`.

Risks: control transfers are state-machine sensitive. Wrong ACK direction, missing requests, stale queued requests, or setup packets arriving during non-token states can cause stalls. The code includes a workaround for hardware returning wrong OUT lengths. `ast_vhub_ep0_queue` rejects requests without completion callbacks unless internal, and rejects queues in token/stall states.

Test signals: enumerate the root hub and downstream gadgets, exercise standard device and hub requests, class hub requests, IN/OUT control transfers with zero, short, exact, and multi-packet data, force stalls and dequeues, send setup during pending data, reset ports, and run with debug logs to verify state transitions token/data/status/stall.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/ep0.c -->
