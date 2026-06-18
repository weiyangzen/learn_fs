# sources/distributed-fs/ceph-client/drivers/usb/chipidea/debug.c

Purpose: implements ChipIdea debugfs diagnostics for gadget/device state, port test mode, queue heads, queued requests, OTG FSM variables, and core registers.

Important APIs/types/functions: provides show/write handlers for `device`, `port_test`, `qheads`, `requests`, optional `otg`, and `registers`, plus exported internal hooks `dbg_create_files` and `dbg_remove_files`.

Control flow: `dbg_create_files` creates a debugfs directory named after the device under `usb_debug_root` and installs files. Reads snapshot controller state, often under spinlock and runtime PM. `port_test` write parses a numeric mode and calls `hw_port_test_set`. Remove looks up and removes the directory.

State and persistence: debugfs files do not own state; they expose live `struct ci_hdrc`, gadget driver, endpoint queue-head/TD DMA contents, OTG FSM variables, and MMIO registers. Port-test write mutates hardware test mode.

Dependencies and integration: depends on debugfs, seq_file, runtime PM, gadget/OTG structures, queue-head/TD definitions from UDC code, and register helpers from `ci.h`/`bits.h`.

Risks: qhead/request dumps cast DMA structures to `u32` streams and are only meaningful in gadget mode. `registers` refuses access in low-power mode to avoid unsafe MMIO. Debugfs creation return values are not checked, so missing files are non-fatal.

Test signals: manual debugfs reads in host/gadget/OTG modes, port-test write validation, low-power register read rejection, and queue/request visibility during active gadget transfers.
