# Group Research: illumos USB host-controller and hub headers subset A

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/illumos/illumos-gate`.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehcid.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehcid.h

EHCI driver-private header for USB 2.0 host-controller state. It defines `ehci_state_t`, per-pipe private state, transfer wrappers for QTD and ITD-based transfers, bandwidth accounting, kstats, controller lifecycle states, DMA pool sizing, register access macros, and public driver-internal prototypes.

Key responsibilities are asynchronous/periodic schedule tracking, descriptor-pool ownership, root-hub integration, polled console I/O state, frame-number overflow tracking, transfer timeout lists, and HCDI entry points for control, bulk, interrupt, and isochronous transfers.

Concurrency is centered on `ehci_int_mutex`, with Warlock annotations documenting lock protection and stable unlocked fields. The file is a central contract between EHCI attach/init, transfer scheduling, interrupt handling, root-hub emulation, and polled-mode console support.

Important implementation constraints include fixed QH/QTD/ITD pool sizes, DMA sync macros, 20 KiB QTD transaction limit, split-transaction bandwidth constants, and vendor-specific PCI workarounds for NVIDIA, ALI/ULi, NEC combo, and VIA controllers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehcid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/openhci/ohci.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/openhci/ohci.h

OHCI hardware-facing header. It defines operational registers (`ohci_regs_t`), register bit masks, the Host Controller Communications Area (`ohci_hcca_t`), endpoint descriptors (`ohci_ed_t`), transfer descriptors (`ohci_td_t`), and isochronous DMA-buffer metadata.

The file captures the shared HCD/HC memory layout and register protocol: control/status registers, list-head registers, frame registers, root-hub registers, HCCA interrupt table and done-head handling, ED state, TD condition codes, and control-transfer phase markers.

It also establishes DMA alignment and scatter/gather constraints, including ED/TD/HCCA alignment and architecture-specific DMA attribute maxima. The ULI1575 workaround constants show reset-time hardware cleanup requirements for registers that do not return to defaults.

This is a low-level ABI header between software and OHCI hardware; mistakes here affect DMA layout, MMIO interpretation, done-list parsing, and root-hub port status handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/openhci/ohci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/openhci/ohci_hub.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/openhci/ohci_hub.h

OHCI root-hub private state header. It defines `ohci_root_hub_t`, which caches the hub descriptor, root-hub descriptor registers, hub/port status, per-port state, control and interrupt pipe handles, current requests, saved interrupt request, and interrupt-pipe timer.

It also defines OHCI root-hub port states: uninitialized, powered off, disconnected, disabled, enabled, and suspended. `OHCI_RH_POLL_TIME` sets the root-hub polling interval.

The file is consumed by the OHCI driver-private state in `ohcid.h` and root-hub request handling code. It translates hardware root-hub registers into USBA hub-class behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/openhci/ohci_hub.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/openhci/ohci_polled.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/openhci/ohci_polled.h

OHCI polled-mode support header for console input/output during firmware/debugger contexts. It defines raw keyboard buffer sizing, input/output mode flags, in-use flags, and `ohci_polled_t`.

`ohci_polled_t` stores the owning controller, input pipe, dummy and interrupt EDs, scan-code buffer, saved done-head fragments, nested polled-entry count, USB device/endpoint identity, and a no-sync workaround flag.

The design explicitly supports nested entry/exit paths such as kmdb to firmware prompt and back. Warlock annotations mark fields protected by polled-mode execution rather than normal mutexes.

This file is critical for keeping OS-mode interrupt processing and polled-mode keyboard access from corrupting each other.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/openhci/ohci_polled.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/openhci/ohcid.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/openhci/ohcid.h

OHCI driver-private header. It defines missed-interrupt bookkeeping, `ohci_state_t`, per-pipe state, transfer wrappers, controller lifecycle states, descriptor-pool flags, timing constants, bandwidth constants, register/DMA access macros, kstats, debug masks, and internal function prototypes.

The controller state covers DDI/USBA registration, PCI/config/MMIO handles, interrupt allocation, HCCA and ED/TD DMA pools, bandwidth arrays, reclaim lists, root hub, timeouts, frame overflow, SOF/error counters, polled-mode saved register/table state, and kstat handles.

Transfer state is represented by `ohci_pipe_private_t` and `ohci_trans_wrapper_t`, including TD lists, DMA cookies, timeout queue linkage, isochronous packet descriptors, and callback dispatch.

The file documents the operational/error/suspend state model and explicitly records lock ordering between OHCI, USBA pipe, device, and pipe-handle locks. It is the main internal integration point for OHCI scheduling, interrupt completion, root-hub requests, and polled console support.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/openhci/ohcid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhci.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhci.h

UHCI hardware and descriptor-layout header. It defines UHCI controller registers (`hc_regs_t`), command/status/interrupt/port bits, MMIO accessor wrappers, queue heads, transfer descriptors, TD field extract/set macros, frame-list sizing, pointer masks, TD status/PID constants, and bandwidth constants.

The descriptor structures include both hardware-controlled fields and software-only linkage used for queues, outstanding TD tracking, transfer-wrapper association, and isochronous scheduling.

The file sets UHCI-specific limits: 1024 frame-list entries, 64 interrupt QH lists, 16-byte QH/TD alignment, maximum bulk TDs per transfer, 1024 isochronous frames, and low-speed/full-speed bandwidth assumptions.

It is the hardware contract consumed by `uhcid.h`, `uhciutil.h`, and transfer scheduling code. Correct field packing and bit operations are essential because UHCI uses compact, bitfield-heavy TD words.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhcid.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhcid.h

UHCI driver-private state header. It defines root-hub state, `uhci_state_t`, DMA binding flags, polled-mode flags, per-pipe state, transfer wrapper state, DMA address conversion macros, kstats, controller lifecycle states, and debug masks.

`uhci_state_t` tracks DDI/USBA registration, MMIO/config handles, interrupt state, frame-list DMA, TD/QH pools, open/close serialization, root-hub timer state, command timeout handling, bandwidth arrays, outstanding TD queues, control/bulk queue heads, SOF synchronization, polled frame table state, software frame number, pending bulk commands, logging, kstats, and debug I/O base.

`uhci_trans_wrapper_t` carries DMA buffer metadata, TD chains, callback state, byte counters, timeout counters, isochronous buffers, bulk/isoc TD pools, and claim state to prevent duplicate deallocation.

The file encodes UHCI’s simpler controller state machine: init, suspend, operational, and error. Lock annotations mirror the other HCDs and make `uhci_int_mutex` the main state guard.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhcid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhcihub.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhcihub.h

UHCI root-hub helper header. It declares root-hub initialization, control request handling, status-change callback, interrupt-pipe cleanup, and interrupt-pipe resource allocation.

It also defines small command constants for port enable/disable operations and port power enable/disable actions.

This file is intentionally narrow: it exposes just enough root-hub behavior for UHCI core and utility code without defining the full root-hub state, which lives in `uhcid.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhcihub.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhcipolled.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhcipolled.h

UHCI polled-mode header. It defines raw buffer sizing, input/output mode flags, in-use flags, low-speed keyboard capacity constant, and `uhci_polled_t`.

The polled state stores the controller, pipe handle, interrupt QH, polling TD, input buffer, polled flags, and nested-entry counter. Warlock annotations state that key fields are only accessed in polled mode.

It declares polled input/output HCDI entry points and a few helper routines used during init/fini paths, including state lookup, queue-head allocation, and transfer-wrapper freeing.

The file supports keyboard/console access when normal interrupt scheduling cannot be used.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhcipolled.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhcitgt.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhcitgt.h

UHCI shared internal prototype header for target-side scheduling and cleanup helpers. It declares queue-head allocation/state lookup, insertion of control, bulk, interrupt, and isochronous TDs, QH insertion/removal, active-bit modification, bandwidth allocation/deallocation, TD/TW removal, isochronous receive polling, data-toggle save, root-hub helpers, callbacks, and periodic IN resource allocation.

This header ties together UHCI transfer construction, endpoint scheduling, bandwidth accounting, root-hub behavior, and callback completion paths.

It contains no structures beyond prototypes; its value is as an internal linkage contract among UHCI implementation files.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhcitgt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhciutil.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhciutil.h

UHCI utility and HCDI prototype header. It declares public HCDI pipe operations, transfer-size queries, frame-number and isochronous-packet queries, root-hub request handling, TD completion handlers, submitted-TD processing, DMA/pool/controller/register setup and teardown, bandwidth handling, transfer-wrapper lifecycle, timeout handling, transfer insertion helpers, isochronous helpers, kstat creation/destruction, and small arithmetic helpers.

This is the broadest UHCI prototype surface and is consumed across attach/init, HCDI, control/bulk/intr/isoc transfer, interrupt, timeout, and statistics code.

It separates function declarations from the descriptor/state definitions in `uhci.h` and `uhcid.h`, keeping the driver’s internal compilation units aligned on shared entry points.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhciutil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/xhci/xhci.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/xhci/xhci.h

Main xHCI driver-private header. It defines DMA policy, transfer and ring structures, device/context structures, event and command rings, endpoint/device/pipe state, USBA integration state, attach sequencing, controller state, polled I/O state, quirks, capabilities, and internal function prototypes.

The design is ring-centric: command, event, and transfer rings use `xhci_ring_t`; `xhci_transfer_t` maps USB requests to TRBs and DMA buffers; `xhci_endpoint_t` owns scheduling state and a transfer ring; `xhci_device_t` owns input/output contexts and endpoint pointers.

`xhci_t` aggregates DDI/PCI/MMIO state, register offsets, capabilities, quirks, interrupt handle, DCBAA, scratchpad buffers, command/event rings, taskq entry, controller lock/cv, and USBA root-hub/device/pipe lists.

The file documents important resource limits: 64 KiB TRB transfer chunks, 63 SGL entries for transfer DMA, 512 KiB advertised max transfer, one interrupt by default, interrupt moderation, periodic transfer buffering, endpoint serialization states, and polled-mode persistent error handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/xhci/xhci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/xhci/xhci_ioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/xhci/xhci_ioctl.h

Private xHCI ioctl header. It defines the ioctl command namespace and three private commands: read port status/control registers, set port link state, and clear port state.

The structures are `xhci_ioctl_portsc_t`, containing up to 256 `PORTSC` values, `xhci_ioctl_setpls_t`, containing a port and target port-link state, and `xhci_ioctl_clear_t`, containing a port.

This is a small diagnostic/control surface. Because it exposes low-level port manipulation, implementation code using it must validate port indices and carefully preserve write-one-to-clear register semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/xhci/xhci_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/xhci/xhcireg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/xhci/xhcireg.h

xHCI register and bitfield definition header, under a permissive BSD-style license from upstream authors plus Joyent copyright. It defines PCI config offsets, capability registers, operational registers, runtime registers, doorbells, extended capability IDs, legacy ownership bits, supported protocol fields, slot and endpoint context field macros, TRB field macros, TRB types, and completion codes.

The header is pure constants/macros and has no driver state. It is used by `xhci.h` and implementation files to parse controller capabilities, program MMIO registers, construct contexts, construct TRBs, decode events, and handle completion status.

Important correctness areas are field shift/mask helpers, port-status write semantics, event-ring register layout, doorbell targeting, endpoint type encodings, TRB cycle/type/slot/endpoint fields, and completion-code mapping.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/xhci/xhcireg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hubd/hub.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hubd/hub.h

USB hub protocol definition header. It defines USB 2 hub descriptors, packed USB 3 SuperSpeed hub descriptors, root-hub descriptor constants, hub-characteristic bits, class request types, hub and port status/change bits, feature selectors, USB 3 status extensions, and remote wake mask values.

The file normalizes the hub-class vocabulary used by physical hub drivers and HCD root-hub emulation. It includes compatibility notes for USB 2 versus USB 3 differences, especially port power/status bit location and extended USB 3 link/config changes.

Important limits include `MAX_PORTS` set to 31 for current hubd simplicity, while USB specifications allow more. xHCI private ioctls separately allow 256 port status slots for controller diagnostics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hubd/hub.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hubd/hubd_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hubd/hubd_impl.h

Hub driver ioctl/devctl implementation header for USB cfgadm integration. It defines `DEVCTL_AP_CONTROL` subcommands for retrieving cfgadm name, current configuration, device path, and refreshing the USB device database, plus string descriptor sub-options.

It defines native and 32-bit-compatible `hubd_ioctl_data` layouts with command, port, get-size flag, user buffer pointer, buffer size, and reserved argument.

The file is an ioctl ABI bridge between userland cfgadm tooling and hubd internals. Its main compatibility concern is preserving structure layout and correct 32-bit pointer handling on 64-bit kernels.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hubd/hubd_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hubd/hubdvar.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hubd/hubdvar.h

Hub driver private state header. It defines hub power state, CPR callback state, main `hubd_t` soft state, hotplug/reset thread arguments, offline request records, init flags, child/port state flags, interrupt-pipe states, cfgadm states, power-budget constants, USB 3 route-depth limit, debug masks, and shared hubd interfaces.

`hubd_t` tracks device state, USBA device data, default and interrupt pipes, normalized hub characteristics, child devinfo and USBA device arrays, port change/reset/state/raw tracking, condition variables, NDI events, CPR callback, hotplug statistics, minor ancestry, cleanup/deathrow state, power budgeting, and optional child cleanup hook.

Concurrency is guarded by `h_mutex`, with Warlock annotations for hub and power data. The state diagram in comments documents transitions among online, disconnected, suspended, powered-down, recovery, and child power-level states.

This is the core hotplug, power-management, event, and cfgadm state contract for hubd.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hubd/hubdvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/scsa2usb/scsa2usb.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/scsa2usb/scsa2usb.h

USB mass-storage SCSI bridge private header. It defines device limits, transfer limits, many vendor/product quirk IDs, quirk attribute flags, power state, last-command tracking, configuration overrides, main `scsa2usb_state_t`, command protocol flags, state macros, SCSA conversion macros, auto-request-sense helpers, CPR callback state, per-command state, CDB field extraction helpers, READ CAPACITY layout, CD block-size helpers, debug masks, and minor-number mapping for ugen support.

`scsa2usb_state_t` is the main per-device object: it tracks USB/SCSI state, transport ownership, mutex/cv, SCSI transport and current packet, per-LUN wait queues/inquiry/devinfo/capacity, endpoint descriptors and pipe handles, packet/pipe state, max HCD bulk transfer, command protocol, work thread, override state, warning suppression, not-ready state, ugen handle, and clone minors.

The header is heavily compatibility-oriented. Quirk flags handle broken GET_MAX_LUN, power management, START_STOP, MODE SENSE, INQUIRY, CSW residue, media checks, and capacity adjustment behavior.

Correctness concerns include command serialization, reset/busy state tests, CDB byte extraction, transfer-size limits, and avoiding repeated timeout-heavy commands for known broken firmware devices.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/scsa2usb/scsa2usb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usb_ia/usb_iavar.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usb_ia/usb_iavar.h

USB Interface Association driver private state header. It defines `usb_ia_t`, init-state flags, child event flags, and debug masks.

`usb_ia_t` tracks instance/init state, mutex, devinfo, common USB power state, device state, first interface, number of grouped interfaces, per-child event registration, child devinfo array, child-list length, logging handle, USB registration data, and NDI event handle.

This driver groups multiple USB interfaces that belong to an interface association. Its state is smaller than `usb_mid_t` because it focuses on an associated interface range rather than generic multi-interface device management.

Concurrency is guarded by `ia_mutex`, with annotations for stable unlocked fields and shared `usb_common_power_t`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usb_ia/usb_iavar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usb_mid/usb_midvar.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usb_mid/usb_midvar.h

USB multi-interface driver private state header. It defines `usb_mid_t`, minor-number encoding macros for ugen support, init-state flags, child event flags, and debug masks.

`usb_mid_t` tracks instance/init state, ugen open count, mutex, devinfo, common power state, USBA device, softstate/device state, interface count, per-child event registration, child interface numbers, child devinfo array, removal/attach counters, logging, USB registration data, NDI event handle, and ugen handle.

This header supports devices whose multiple interfaces are split into child nodes. It handles both normal child event tracking and generic user-level access through ugen minor allocation.

Concurrency uses `mi_mutex`; Warlock annotations identify stable data readable without the lock.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usb_mid/usb_midvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba.h

Top-level USBA client-driver include wrapper. It pulls in common kernel/DDI headers needed by USB client drivers and then includes `<sys/usb/usbai.h>`.

The file defines no driver state, constants, or functions of its own beyond include guards and C++ linkage wrapping. Its role is dependency aggregation for USB client-driver interfaces.

Because it is broad and public-facing, changes here have large compile-time and API-surface impact across USB drivers. It should remain minimal and stable.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba.h -->