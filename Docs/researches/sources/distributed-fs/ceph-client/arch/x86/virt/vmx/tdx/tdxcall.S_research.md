# sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/tdxcall.S

Purpose: Implements the assembly glue for TDCALL and SEAMCALL through the shared `TDX_MODULE_CALL` macro, moving C `struct tdx_module_args` fields into ABI registers, invoking the instruction, optionally saving return registers, handling SEAMCALL faults, and preserving the x86-64 ABI.

Important APIs/types/functions: The file defines instruction bytes for `tdcall` and `seamcall` and a parameterized `TDX_MODULE_CALL host ret saved` macro. The macro supports normal calls, calls that return output registers, and calls requiring callee-saved registers for large ABIs such as VP.ENTER.

Control flow and state: Inputs arrive with leaf in `%rdi` and args pointer in `%rsi`. The macro loads RAX/RCX/RDX/R8-R11 and optionally RBX/RDI/RSI/R12-R15, saves callee-saved registers, executes SEAMCALL or TDCALL, copies outputs back to the args structure when requested, clears shared guest/VMM registers on saved-return paths to reduce speculative exposure, restores saved registers, and returns RAX status. SEAMCALL CF is normalized to `TDX_SEAMCALL_VMFAILINVALID`; #GP/#UD traps are converted to TDX software error codes through an exception table.

Dependencies and integration points: It uses asm offsets for `struct tdx_module_args`, frame macros, exception table annotations, and status constants from `asm/tdx.h`. It is the low-level backend for host TDX wrappers in `tdx.c` and guest TDX code elsewhere.

Risks and test signals: Register save/restore errors can corrupt callers or leak guest-controlled values. Fault mapping must distinguish absent/busy SEAM firmware from real module status. Objtool/noinstr constraints matter for VP.ENTER paths. Test signals include successful TDH.SYS.* calls, injected SEAMCALL #UD/#GP handling, VP.ENTER register round trips, kexec/noinstr validation, and absence of callee-saved register corruption.
