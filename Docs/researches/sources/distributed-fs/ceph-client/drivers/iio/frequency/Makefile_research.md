# sources/distributed-fs/ceph-client/drivers/iio/frequency/Makefile

Purpose: Kbuild object list for IIO frequency drivers.

Important targets: maps each Kconfig symbol to its object: `ad9523.o`, `adf4350.o`, `adf4371.o`, `adf4377.o`, `admfm2000.o`, `admv1013.o`, `admv1014.o`, `admv4420.o`, and `adrf6780.o`.

Control flow: Kbuild includes objects according to selected config symbols. The file is alphabetically ordered as requested by its comment.

State/persistence: no runtime state.

Dependencies/integration: consumes frequency Kconfig symbols and compiles the corresponding drivers into the kernel or modules.

Risks: missing object additions for new Kconfig entries would silently omit drivers. Test signals are module/built-in build coverage for each symbol and ordering checks during review.
