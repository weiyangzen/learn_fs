# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/nvme_err

Symlink to `smart`; behavior is selected by invoked basename `nvme_err`.

Behavior:
- Detects NVMe SMART/health output.
- Extracts `Media and Data Integrity Errors` into `nvme_err=<count>`.
- Emits `nvme_err=` when unavailable.

Role:
- Reports NVMe media/data integrity error count.
