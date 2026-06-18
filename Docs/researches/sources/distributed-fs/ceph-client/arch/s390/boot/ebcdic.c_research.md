<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/ebcdic.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/ebcdic.c

Purpose: reuses the s390 EBCDIC/ASCII conversion tables and helpers in early boot. Important content is the include of `../kernel/ebcdic.c`, which provides conversion macros/functions used for boot command-line handling. Control flow is inherited; this wrapper compiles the kernel implementation with boot flags. State is conversion table data; no persistence. Dependencies include `ipl_parm.c`, boot C flags, and s390 encoding conventions. Risks are shared implementation gaining runtime-only dependencies, table changes affecting IPL parameter interpretation, and duplicate symbols. Test signals: EBCDIC command-line conversion, VM reader/IPL parameter data, decompressor link, and boot with non-ASCII parameter records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/ebcdic.c -->
