# sources/distributed-fs/openafs/src/tools/dumpscan/backuphdr.c

Purpose: generic backup-system header adapter for dumpscan, currently recognizing old Stage backup headers and exposing them as `backup_system_header`.

Important APIs/functions: `try_backuphdr` is registered as a special top-level parser for `STAGE_VERSMIN`. It calls `ParseStageHdr`, optionally prints via `PrintBackupHdr`, invokes `cb_bckhdr`, seeks back after callbacks when `DSFLAG_SEEK` is set, and frees allocated strings. `PrintBackupHdr` formats version, volume, location, dump range, dump time, flags, length, and tape file number.

State/dependencies: no persistent state; it allocates transient strings inside `backup_system_header` via `stagehdr.c`. It depends on `dumpscan.h`, `dumpscan_errs.h`, `stagehdr.h`, time formatting, and parser callback conventions.

Risks/test signals: only Stage headers are recognized; unknown backup headers return `DSERR_MAGIC`. Callback consumers must copy header data if needed because storage is freed before return. The printed length path differs for native and struct-based `dt_uint64`.
