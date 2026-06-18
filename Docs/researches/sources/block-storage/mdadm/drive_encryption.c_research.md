# File Research: sources/block-storage/mdadm/drive_encryption.c

## Purpose
`drive_encryption.c` probes NVMe and ATA/SATA drives for encryption ability and lock status, including Opal self-encrypting drives and ATA standard security.

## Main Flow
For NVMe, `get_nvme_opal_encryption_information()` checks optional admin command support, checks supported security protocols, reads Opal Level 0 discovery with `NVME_IOCTL_ADMIN_CMD`, and extracts the Opal locking feature.

For ATA/SATA, `get_ata_encryption_information()` reads ATA identify data through SG_IO ATA PASS-THROUGH(12), optionally verifies Opal support through trusted-computing/security-protocol checks, requires `libata.allow_tpm=1` unless disabled by config, then either parses Opal Level 0 discovery or falls back to ATA security status.

## Key Behavior
- Encryption ability maps to `None`, `Other`, or `SED`.
- Encryption status maps to `Unencrypted`, `Locked`, or `Unlocked`.
- Opal locking feature parsing follows variable-length discovery feature records and uses big-endian feature codes/lengths.
- NVMe support is gated by OACS bit 0 and security protocol `0x01`.
- ATA standard security reports `Other` ability when ATA security is supported but Opal is not confirmed.
- SATA Opal verification can be skipped by `ENCRYPTION_NO_VERIFY sata_opal` config.

## Integration Notes
The file uses Linux NVMe ioctls, SCSI generic `SG_IO`, ATA PASS-THROUGH sense validation, mdadm verbose logging, fd-to-kernel-name helpers, sysfs libata TPM checks, and config accessors.

## Risks
The probing path depends on device/driver support and can fail on permission, kernel config, libata TPM policy, or transport translation quirks. The code uses packed bitfields over endian-converted words, so compiler/layout assumptions matter.
