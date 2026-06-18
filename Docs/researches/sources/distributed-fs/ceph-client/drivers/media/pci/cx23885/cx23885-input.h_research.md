# Research: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-input.h

Purpose: Internal header for cx23885 IR input support.

Important APIs/types/functions: declares `cx23885_input_rx_work_handler()`, `cx23885_input_init()`, and `cx23885_input_fini()`.

Control flow: the core and IR notification files include this header to register the rc-core device at probe, pass RX events from workqueue context, and tear down input state at remove.

State and persistence: no state is defined in the header. It exposes functions that operate on `struct cx23885_dev`.

Dependencies/integration: guarded by `_CX23885_INPUT_H_`; assumes `struct cx23885_dev` and `u32` are declared by the including context, usually `cx23885.h`.

Risks: narrow internal ABI, so include order matters. Missing this header would not affect external kernel APIs but would break coordination between core, IR, and input code.

Test signals: compile coverage and successful IR init/fini paths on supported boards.
