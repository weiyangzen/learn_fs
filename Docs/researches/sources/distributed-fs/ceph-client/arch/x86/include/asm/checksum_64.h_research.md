
# sources/distributed-fs/ceph-client/arch/x86/include/asm/checksum_64.h

Purpose: x86-64 internet checksum primitives and declarations.

Important APIs and control flow: inline helpers fold 32-bit sums, compute fast IPv4 header checksums, build TCP/UDP pseudo-header sums, add checksums with carry, and compute IPv6 pseudo-header checksums using 64-bit add/adc. Bulk checksum/copy routines are external assembly/C functions: `csum_partial`, `csum_partial_copy_generic`, user copy wrappers, unchecked copy, and `ip_compute_csum`.

State, dependencies, and risks: state is transient sum/carry handling and user access in external routines. Dependencies include byteorder, IPv6 types, and low-level checksum implementations. Risks include mixing folded/unfolded sums, assuming 64-bit alignment, and user-copy exception paths. Test signals are network stack checksum tests, IPv4/IPv6 packet validation, and uaccess fault tests.
