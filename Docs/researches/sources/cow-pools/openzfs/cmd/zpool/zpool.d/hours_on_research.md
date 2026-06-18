# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/hours_on

Symlink to `smart`; behavior is selected by invoked basename `hours_on`.

Behavior:
- Parses SMART power-on time for SAS, SATA, and NVMe.
- SAS: `number of hours powered up`.
- SATA: `Power_On_Hours`.
- NVMe: `Power On Hours`, with punctuation stripped.
- Prints `hours_on=<hours>` or `hours_on=`.

Role:
- Reports drive lifetime powered-on hours.
