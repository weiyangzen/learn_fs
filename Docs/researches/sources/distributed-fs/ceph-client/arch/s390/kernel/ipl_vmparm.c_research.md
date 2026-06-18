# sources/distributed-fs/ceph-client/arch/s390/kernel/ipl_vmparm.c

Purpose: converts the VM IPL parameter field from an IPL parameter block into a NUL-terminated ASCII string.

Important API: `ipl_block_get_ascii_vmparm(char *dest, size_t size, const struct ipl_parameter_block *ipb)` checks the CCW VM parameter-present flag and length, copies at most `size - 1` bytes, normalizes all-uppercase EBCDIC to lowercase EBCDIC when no lowercase is present, converts from EBCDIC to ASCII, terminates the buffer, and returns the copied length.

Control flow and state: this file is stateless. It only reads `ipb->ccw.vm_flags`, `vm_parm_len`, and `vm_parm`. The lowercase detection scans EBCDIC lowercase byte ranges before applying `EBC_TOLOWER()` and `EBCASC()`.

Dependencies and integration: used by `ipl.c` for `/sys/firmware/ipl/parm` and reipl VM parameter display. Depends on `asm/ipl.h` layout and EBCDIC helpers.

Risks and test signals: callers must pass nonzero `size`, because the function computes `size - 1`. Test empty/no-flag cases, maximum `DIAG308_VMPARM_SIZE`, mixed case preservation, uppercase normalization, and sysfs display consistency after reipl parameter writes.
