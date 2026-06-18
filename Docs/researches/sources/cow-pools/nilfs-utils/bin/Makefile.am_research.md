# File Research: sources/cow-pools/nilfs-utils/bin/Makefile.am

Builds NILFS user commands: `chcp`, `dumpseg`, `lscp`, `lssu`, `mkcp`, and `rmcp`. It uses `-Wall`, includes `$(top_srcdir)/include`, and links most tools against `libnilfs.la`.

Per-tool link additions show dependencies: `chcp` and `rmcp` use `libparser.la`; `dumpseg` uses `libsegment.la`; `lssu` uses `libnilfsgc.la` and `libparser.la`; `mkcp` and `chcp` use POSIX semaphore libs via `$(LIB_POSIX_SEM)`.
