# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/smartx

Symlink to `smart`; behavior is selected by invoked basename `smartx`.

Behavior:
- Provides extended SMART fields based on drive type.
- SAS: `hours_on`, `defect`, `nonmed`, `r_proc`, `w_proc`.
- SATA: `hours_on`, `pwr_cyc`.
- NVMe: `hours_on`, `pwr_cyc`.
- Prints empty values for missing fields.

Role:
- Complements `smart` with secondary lifetime and diagnostic metrics.
