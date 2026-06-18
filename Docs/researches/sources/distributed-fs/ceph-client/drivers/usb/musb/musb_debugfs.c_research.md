# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_debugfs.c

Purpose: implements debugfs observability and manual controls for MUSB controllers. It exposes register dumps, USB test mode selection, and host soft-connect control under a per-controller debugfs directory.

Important APIs, types, and functions: `struct musb_register_map` and `musb_regmap` list core and DMA register names, offsets, and widths. `musb_regdump_show` reads and prints the register map under a runtime-PM reference. Test mode support is implemented by `musb_test_mode_show`, `musb_test_mode_open`, and `musb_test_mode_write`; it writes `MUSB_TESTMODE` and loads the USB test packet for "test packet". Soft-connect support is `musb_softconnect_show`, `musb_softconnect_open`, and `musb_softconnect_write`; it reads/updates DEVCTL SESSION and can call `musb_root_disconnect`. `musb_init_debugfs` creates files `regdump`, `testmode`, and `softconnect`; `musb_exit_debugfs` removes the directory tree.

Control flow: during core init, `musb_init_debugfs` creates a directory named after the controller under `usb_debug_root`. Reading `regdump` resumes the device, snapshots all listed registers with width-appropriate accessors, and autosuspends. Writing `testmode` copies a short user string, refuses changes if a test mode is already active, maps recognized strings to test bits, optionally writes the test packet to ep0 FIFO, then writes TESTMODE. `softconnect` only reports meaningful state for host A states and writing `0` or `1` clears or sets DEVCTL SESSION for selected host states.

State and persistence: debugfs files are runtime-only and disappear on remove/unmount. Writes affect hardware registers, `musb->context.devctl`, and root-hub connection state; there is no disk persistence.

Dependencies and integration points: depends on debugfs, seq_file, uaccess, MUSB register accessors, runtime PM, USB debug root, and host/gadget helper functions. It integrates with USB electrical compliance testing and manual host connection simulation.

Risks: debugfs writes directly affect controller state and can disrupt active transfers. `testmode` accepts unrecognized strings by leaving `test` at its previous value and still writing it, so invalid input may be a silent no-op. Register dump offsets include generic DMA registers that may not exist on all wrappers. Runtime-PM get return values are not checked in these debug paths. Softconnect logic is host-state-specific and will ignore writes in most other states.

Test signals: build with debugfs enabled, read `regdump` during idle and active transfers, write every supported test mode after USB reset, verify "test packet" loads ep0 FIFO, attempt second testmode write and invalid strings, exercise `softconnect` in A_HOST and A_WAIT_BCON, and remove the device while debugfs files are open.
