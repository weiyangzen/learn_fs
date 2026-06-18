# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr.h

Purpose: defines the version-independent MFC hardware operation interface and the register pointer map used by newer hardware backends.

Important APIs and types: `struct s5p_mfc_regs` contains `void __iomem *` pointers for common, decoder, and encoder registers across v6 through v12, including fields only present on selected versions. `struct s5p_mfc_hw_ops` is the driver-wide hardware abstraction, covering buffer allocation/release, DPB/source-size calculation, encoder stream/source buffer programming, scheduler `try_run`, interrupt flag clearing, decoder/encoder status getters, error decoding, crop/picture metadata getters, and scratch-size getters. Exported functions initialize ops/registers and allocate/release private or generic buffers.

Control flow: core code calls `s5p_mfc_init_hw_ops` and then invokes hardware methods with `s5p_mfc_hw_call`. Version-specific files fill this table with v5 or v6+ implementations. v6+ code also fills `struct s5p_mfc_regs` so later code can use symbolic pointer fields rather than raw offsets.

State and persistence: the header declares structure layouts only. Runtime state lives in `dev->mfc_ops`, `dev->mfc_regs`, and allocation buffers owned by `struct s5p_mfc_dev` or `struct s5p_mfc_ctx`.

Dependencies and integration points: includes `s5p_mfc_common.h` and is included by command, encoder, decoder, power/scheduler, and version-specific operation files. It is the primary interface between generic V4L2/context code and SoC-version register programming.

Risks: operation-table evolution is high risk because every version backend must populate compatible callbacks. `struct s5p_mfc_regs` contains many version-conditional fields, so callers must avoid using uninitialized fields on unsupported hardware. The interface mixes encoder, decoder, buffer-management, and status access, which makes regressions broad when signatures change.

Test signals: compile coverage for all supported MFC variants; static checks for initialized operation fields; runtime encode/decode on v5, v6/v7/v8, v10, and v12 devices; and fault-injection around allocation/release helpers.
