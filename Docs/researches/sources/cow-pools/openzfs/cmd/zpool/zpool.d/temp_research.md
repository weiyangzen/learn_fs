# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/temp

Symlink to `smart`; behavior is selected by invoked basename `temp`.

Behavior:
- Parses temperature from SAS `Drive Temperature`, SATA temperature attributes/current temperature, or NVMe `Temperature`.
- Prints `temp=<celsius>` or `temp=`.

Role:
- Reports drive temperature as a standalone custom column.
