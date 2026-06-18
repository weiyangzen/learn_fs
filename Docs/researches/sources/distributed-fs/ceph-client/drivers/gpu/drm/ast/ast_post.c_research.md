<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_post.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_post.c

## Purpose

`ast_post.c` contains AST DRM driver's low-level POST helpers that route memory-mapped register access through the device's DWM window and dispatch generation-specific GPU initialization. It also exposes small memory-controller test helpers used by the AST POST implementations.

## Important APIs, Types, And Functions

- `__ast_mindwm(void __iomem *regs, u32 r)` and `__ast_moutdwm(void __iomem *regs, u32 r, u32 v)`: raw helpers that select the 64 KiB DWM aperture by writing the high address bits to `0xf004`, trigger selection through `0xf000`, poll until the selected window matches, then read or write `0x10000 + low16(r)`.
- `ast_mindwm()` and `ast_moutdwm()`: `struct ast_device` wrappers around the raw helpers.
- `ast_post_gpu(struct ast_device *ast)`: chooses `ast_2600_post`, `ast_2500_post`, `ast_2300_post`, `ast_2100_post`, or `ast_2000_post` based on `AST_GEN(ast)`.
- `mmc_test()` and `mmc_test_burst()`: issue memory controller self-test commands at DWM address `0x1e6e0070` and poll for completion/error bits.

## Control Flow

The DWM helpers first program the aperture selector, then spin until the hardware reports the selected high address bits before performing the final register access. `ast_post_gpu()` is a straight generation cascade from newest to oldest with error propagation from the selected POST function. `mmc_test()` clears the test register, starts a test from `datagen` and `test_ctl`, then polls bits `0x3000`: bit `0x2000` or timeout is failure, any completion bit without error is success, and the test control register is cleared before returning.

## State And Persistence Behavior

The file persists no software state. It mutates AST hardware registers: DWM aperture selection, generation-specific POST side effects through called functions, and memory-controller test control/status. A failed `mmc_test()` timeout explicitly clears the test register to leave the controller idle.

## Dependencies And Integration Points

It depends on `ast_drv.h` for device layout, generation detection, and register accessors, and on `ast_post.h` for prototypes. The generation-specific POST functions are implemented in sibling AST source files. The code runs during AST device bring-up before normal KMS operation.

## Risks And Edge Cases

The DWM polling loops have no timeout, so broken register-window selection can hang the caller. `mmc_test()` has a large software timeout but no sleep, so failures can burn CPU during POST. Generation routing depends entirely on correct `AST_GEN()` classification. The DWM helpers assume the caller supplies valid register-window addresses and that `ast->regs` is already mapped.

## Test Signals

Useful signals include probe/POST on AST2000/2100/2300/2500/2600-era hardware, fault injection around POST return codes, memory-controller test pass/fail paths, and boot tests where the DWM aperture is exercised before modeset initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_post.c -->
