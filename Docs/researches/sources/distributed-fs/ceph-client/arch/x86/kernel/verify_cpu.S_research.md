# sources/distributed-fs/ceph-client/arch/x86/kernel/verify_cpu.S

Purpose: assembly helper included by early boot and trampoline code to verify that a CPU supports the minimum features needed for long mode and SSE.

Important APIs/functions: local symbol `verify_cpu` returns `0` in `%eax` for success and `1` for failure. It consumes required feature masks from `cpufeatures.h`/`cpufeaturemasks.h` and MSR constants for Intel and AMD feature enabling.

Control flow: the routine saves flags, clears dangerous flags, optionally verifies CPUID availability on 32-bit, checks CPUID leaf 1 and extended leaf `0x80000001` against required masks, detects AMD and Intel vendors, clears Intel `IA32_MISC_ENABLE_XD_DISABLE` when safe, and attempts to enable SSE on AMD via `MSR_K7_HWCR` before one retry. It restores flags before returning.

State and persistence: normally only registers and flags are temporary. Side effects can include clearing Intel XD disable and enabling AMD SSE through MSR writes; those hardware state changes persist after return.

Dependencies and integration: included by compressed boot, secondary CPU trampoline, and 32-bit startup paths, so it must run in 32-bit code and avoid normal C runtime assumptions. It depends on CPUID, RDMSR/WRMSR, required feature masks, and caller-side error handling.

Risks: this code executes very early with limited diagnostics. Incorrect masks or unsafe MSR access can prevent boot or secondary CPU bringup. Vendor/model checks around XD disable are deliberately narrow to avoid touching unsupported Intel MSRs.

Test signals: successful 64-bit boot and AP bringup on supported CPUs, expected halt/error path on unsupported CPUs, and no early #GP from MSR access. CPU feature mask changes should be validated in boot and trampoline contexts.
