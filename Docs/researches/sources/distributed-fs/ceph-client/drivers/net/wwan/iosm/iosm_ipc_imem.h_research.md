# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_imem.h

Purpose: declares the central IOSM shared-memory model: IPC phases, channel states/types, pipe directions, HP update identifiers, pipe/channel layouts, and the `struct iosm_imem` root object shared across PCIe, protocol, mux, devlink, WWAN, trace, debugfs, timers, and task queues.

Important types/APIs: `ipc_pipe`, `ipc_mem_channel`, `ipc_phase`, and `iosm_imem`; exported functions cover initialization, cleanup, IRQ dispatch, PM suspend/resume/s2idle, channel lifecycle, pipe cleanup/close, TD update timers, UL send, phase update/stringification, feature-set messages, IPC init handshake, and devlink chip-info trigger.

Control flow role: this header defines the invariants the implementation enforces. Channels move FREE -> RESERVED -> ACTIVE -> CLOSING/FREE. Phases progress OFF/ROM/PSI/EBL/RUN or crash/coredump. Pipes carry TD rings and SKB rings with old head/tail tracking. Timers and completions are embedded for asynchronous IRQ/tasklet coordination.

State/dependencies: all state is volatile driver memory except CP state mirrored through MMIO and DMA descriptors shared with the modem. Dependencies include Linux SKB/completion/hrtimer/work_struct plus local MMIO, PCIe, WWAN, uevent, and task-queue APIs. Risks include ABI-size assumptions in SKB control block use, channel count limits, timer state shared through one `hrtimer_period`, and incorrect phase assumptions. Test signals: structure initialization, phase strings, channel bounds, reserved/active transitions, and cleanup clearing subsystem flags.
