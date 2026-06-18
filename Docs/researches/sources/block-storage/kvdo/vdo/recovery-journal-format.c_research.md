# File Research: sources/block-storage/kvdo/vdo/recovery-journal-format.c

Read completely: 164 lines.

This file encodes and decodes the recovery journal component state stored in the VDO superblock. It defines `VDO_RECOVERY_JOURNAL_HEADER_7_0` with component id `VDO_RECOVERY_JOURNAL`, version 7.0, and payload size `sizeof(struct recovery_journal_state_7_0)`.

`vdo_get_recovery_journal_encoded_size()` returns header plus payload size. The encode path writes the component header and three little-endian 64-bit values: journal start sequence, logical blocks used, and block-map data blocks. The decode path validates the header and reads the same fields back, asserting the decoded payload size matches the header. `vdo_get_journal_operation_name()` maps journal operation enum values to diagnostic strings.

Dependencies: VDO buffer encoding helpers, component header validation, status codes, recovery journal format definitions, and packed journal operation enum.

Security/reliability notes: decode validates component identity/version/size before accepting state. Operation names include an unknown fallback for diagnostics.
