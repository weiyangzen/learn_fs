# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_bsun.S

Purpose: implements `fpsp_bsun`, the FPSP entry for branch/set-on-unordered exceptions. It preserves 68881/68882 compatibility by copying the exception PC into the saved user FPIAR before delegating to the real kernel handler.

Important APIs/types/functions: exported label is `fpsp_bsun`. It saves `%d0-%d1/%a0-%a1`, `%fp0-%fp3`, and `%fpcr/%fpsr/%fpiar`, writes `EXC_PC` to `USER_FPIAR`, restores state, `frestore`s the FPU state frame, unlinks, and branches to `real_bsun`.

Control flow: linear handler: allocate local frame, save FPU state and volatile registers, update FPIAR compatibility state, restore everything, then tail-call the OS-level `real_bsun` handler.

State and persistence: no persistence. It mutates only the exception-local saved FPIAR slot before restoring user-visible FPU control registers.

Dependencies/integration: depends on `fpsp.h` frame offsets and the external `real_bsun` kernel entry. The real handler is expected to perform remaining corrective behavior described by the 68040 manual.

Risks: incorrect stack/frame offsets would corrupt the exception frame before transferring to the kernel. Because the code restores FPU state before `real_bsun`, any required FPSP-side state changes must be completed before the branch.

Test signals: trigger BSUN with unordered comparisons, verify FPIAR equals the faulting PC, ensure all saved general/FPU registers are restored, and confirm the OS handler receives the expected integer exception frame.
