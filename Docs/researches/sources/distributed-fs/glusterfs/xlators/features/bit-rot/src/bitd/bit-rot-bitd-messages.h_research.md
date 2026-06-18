<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-bitd-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-bitd-messages.h

## Purpose
Message ID and canonical string catalog for the bit-rot daemon translator.

## APIs, Types, and Functions
Uses `GLFS_MSGID(BITROT_BITD, ...)` to allocate stable message identifiers for fd creation, reads, checksums, signing, changelog registration, crawling, scrub scheduling, corruption marking, bad-object listing, memory, timer, and state-machine events. Also defines string macros for common message text.

## Control Flow, State, and Persistence
No runtime flow. Stability is persistent at the logging ABI level: comments require appending new IDs and never removing old ones to avoid ID reuse.

## Dependencies and Integration
Includes `glusterfs/glfs-message-id.h` and is included by bit-rot daemon sources for `gf_msg()` calls.

## Risks and Test Signals
Risks include accidental ID removal/reordering, typos in strings becoming operator-visible, and missing strings for newer IDs. Test signals are successful compilation of all `gf_msg()` uses and log/message catalog consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-bitd-messages.h -->
