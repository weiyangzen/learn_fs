# sources/distributed-fs/ceph-client/arch/x86/lib/checksum_32.S

Purpose: implements 32-bit x86 Internet checksum routines optimized for IP/TCP/UDP and checksum-with-copy operations.

Important APIs/functions: defines and exports `csum_partial` and `csum_partial_copy_generic`. Two implementation families are compiled depending on `CONFIG_X86_USE_PPRO_CHECKSUM`: a 486/Pentium-oriented loop and a Pentium Pro/II unrolled/nospec dispatch version. Exception macro `EXC` annotates faulting copy instructions for uaccess recovery and clearing `%eax`.

Control flow: `csum_partial` handles odd, 2-byte, and 4-byte alignment first, then accumulates 32-byte or 128-byte chunks with carry using `adcl`, then handles trailing words/bytes and rotates the result if the original buffer was odd-aligned. `csum_partial_copy_generic` copies from source to destination while accumulating checksum, with exception table fixups so faults return a safe value and stop copying. The PPro path uses computed jumps guarded by `JMP_NOSPEC` for unrolled chunk entry.

State and persistence behavior: no global state. It reads packet buffers, writes destination buffers in copy variants, and returns an unfolded checksum. Faults may leave partial destination contents depending on exception point, with wrappers responsible for higher-level handling.

Dependencies/integration points: used by the networking stack on 32-bit x86 when generic checksum is not selected. Depends on Linux exception table formats, uaccess exception typing, export symbols, and nospec branch helpers.

Risks: checksum correctness is sensitive to byte order, odd alignment, carry folding, and tail handling. Exception table labels must match faulting loads/stores. Computed jump tables must be speculation-safe. Any ABI/register-save mistake can corrupt networking data paths.

Test signals: network checksum selftests, packet send/receive with odd and unaligned buffers, fault-injection tests for checksum-copy from/to user memory, and 32-bit builds with both PPro checksum configurations.
