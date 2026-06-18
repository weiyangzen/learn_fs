<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/zbase32.h -->
# sources/cloud-native/ostree/src/libotutil/zbase32.h

## Purpose
Declares the z-base-32 encoder and preserves version metadata from the imported implementation.

## Important APIs and Types
The only callable API is `char *zbase32_encode(const unsigned char *data, size_t length)`. Static version constants describe upstream base32 version 0.9.12.

## Control Flow
No executable control flow exists in the header.

## State and Persistence
No state is stored. The API promises an allocated encoded string for the provided buffer.

## Dependencies and Integration Points
Includes `assert.h` and `stddef.h`. Consumers integrate with the C implementation and must free returned memory according to its allocation strategy.

## Risks
The header-level static version variables appear in every including translation unit; they are harmless but can trigger unused warnings depending on flags. The allocator convention is not GLib-specific.

## Test Signals
Compile/link checks and ownership tests around `zbase32_encode` cover the public contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/zbase32.h -->
