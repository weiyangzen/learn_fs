# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxnv40.h

`ctxnv40.h` defines the tiny builder API used by `ctxnv40.c` and `ctxnv50.c` to emit NV40/NV50-style PGRAPH context programs and default context values. It holds `struct nvkm_grctx` and inline helpers for context-program output, labels, branches, waits, flag updates, position changes, and default register writes.

The key type is `struct nvkm_grctx`, which stores the device, generation mode (`NVKM_GRCTX_PROG` or `NVKM_GRCTX_VALS`), output instruction buffer, GPU object target, program limits/labels, current context register, and context value positions. Helpers are `cp_out()`, `cp_lsr()`, `cp_ctx()`, `cp_name()`, `_cp_bra()` with `cp_bra`/`cp_cal`/`cp_ret`, `_cp_wait()` with `cp_wait`, `_cp_set()` with `cp_set`, `cp_pos()`, and `gr_def()`.

In program mode, helpers append instructions to `ctx->ucode`, track `ctxprog_len`, and resolve forward branch placeholders when `cp_name()` later defines a label. `cp_ctx()` converts MMIO register addresses into context register indexes, advances `ctxvals_pos`, emits long-length load-state-register sequences when needed, and emits a CP context instruction. In value mode, most CP helpers are no-ops; `gr_def()` maps an MMIO register to the reserved context value offset and writes the default into `ctx->data`.

The header depends on `<core/gpuobj.h>` for `struct nvkm_gpuobj` and `nvkm_wo32()`. It relies on CP opcode and flag macros being defined by the including `.c` file before use, which is why `ctxnv40.c` defines `CP_*` values before including it. It integrates with NV40/NV50 context generators as an internal DSL.

Risks include label patching mistakes, unchecked label indexes beyond 32, `BUG_ON()` if a program exceeds `ctxprog_max`, incorrect `ctxvals_pos` accounting, and the implicit dependency on include-order macros. Test signals are successful builds of NV40/NV50 generators, context program generation without `BUG_ON`, correct returned context sizes, and runtime validation on old GPUs that context defaults land at expected offsets.
