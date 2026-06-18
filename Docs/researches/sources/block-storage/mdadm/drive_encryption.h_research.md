# File Research: sources/block-storage/mdadm/drive_encryption.h

## Purpose
`drive_encryption.h` declares mdadm's drive encryption status model and probe API.

## Contents
It defines `encryption_status_t`, `encryption_ability_t`, `encryption_information_t`, and declarations for NVMe Opal probing, ATA probing, and string mapping helpers.

## Integration Notes
Metadata display code can call these helpers to report member drive encryption state without depending on the ioctl details in `drive_encryption.c`.
