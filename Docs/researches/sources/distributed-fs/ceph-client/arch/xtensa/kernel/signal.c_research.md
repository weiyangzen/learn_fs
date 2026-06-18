# sources/distributed-fs/ceph-client/arch/xtensa/kernel/signal.c

Purpose: Implements Xtensa real-time signal delivery and return, preserving user register state, register windows, optional coprocessor state, altstack data, and syscall restart semantics.

Important APIs, types, and functions: `struct rt_sigframe`, `flush_window_regs_user()`, `setup_sigcontext()`, `restore_sigcontext()`, `xtensa_rt_sigreturn()`, `gen_return_code()`, `setup_frame()`, `do_signal()`, and `do_notify_resume()`.

Control flow: Signal setup flushes live register windows to the user stack, copies core/coprocessor/user extension registers into the frame, saves the mask and altstack, installs either a user restorer or generated `rt_sigreturn` instructions, and rewrites `pt_regs` so userspace enters the handler. Return validates the frame, restores the blocked mask, register state, altstack, and returns the saved `a2`. `do_signal()` handles `-ERESTART*` values by either converting to `-EINTR` or rewinding `pc` by the syscall instruction width.

State and persistence: Writes user stack frames, updates current signal mask, `pt_regs`, thread-local Xtensa extension/coprocessor buffers, and restart block function. Generated return code requires explicit I-cache/D-cache synchronization.

Dependencies and integration: Integrates with generic signal core (`get_signal`, `signal_setup_done`), `uaccess`, `resume_user_mode_work`, Xtensa ABI macros, optional FDPIC function descriptors, coprocessor lazy context handling, and cacheflush routines.

Risks: Register-window spill failures become `SIGSEGV`; generated stack code is sensitive to endian encodings and syscall number size; `depc > 64` double-exception paths panic; restoring only selected PS bits is intentional but fragile; FDPIC handler/restorer descriptors must be validated.

Test signals: Exercise SA_SIGINFO, SA_RESTORER, altstack, FDPIC if enabled, syscall restart cases, user stack fault during frame build/return, coprocessor users, windowed and call0 ABIs, and single-step preservation.
