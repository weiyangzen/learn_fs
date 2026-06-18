# sources/distributed-fs/lizardfs/src/protocol/MFSCommunication.h

## Purpose
Defines the core LizardFS/MooseFS wire protocol constants: packet framing, block/chunk geometry, file/object type codes, mode/flag enums, session flags, and command ids with documented payload layouts.

## Important APIs, Types, And Functions
This is a macro/constant header, not an implementation file. It defines packet frame comments (`type:32 length:32 data`), block and chunk masks/sizes (`MFSBLOCKSIZE`, `MFSCHUNKSIZE`, `MFSCHUNKBITS`, etc.), filesystem limits, file type chars, attribute/set flags, session flags, lock operations, xattr modes, server status constants, and hundreds of command IDs across any-to-any, metalogger-master, chunkserver-master, client-chunkserver, chunkserver-chunkserver, client-master, admin, quota, lock, task, tape, and stats protocols. It also defines the C++ `SugidClearMode` enum when not building C/Wireshark code.

## Control Flow
There is no executable control flow. Other protocol headers and components include this file to choose packet ids and interpret payload comments. Static preprocessor checks enforce power-of-two block/chunk assumptions.

## State And Persistence Behavior
No state. The constants define persistent wire compatibility: changing values would break client/master/chunkserver interoperability and stored protocol assumptions.

## Dependencies And Integration Points
Included by mount write code, Ganesha pNFS code, and protocol serializers such as `cltocs.h`, `cltoma.h`, and `cstocl.h`. It is also likely used by master/chunkserver/client implementations and tools.

## Risks And Edge Cases
This is a compatibility-critical registry with legacy and LizardFS-extended IDs interleaved. Duplicate comments/defines appear around chunks health and numeric comments, so maintainers must avoid accidental ID reuse. Payload comments are documentation rather than compiler-checked schemas except where newer serializer headers wrap them. Any change to geometry macros affects cache/write paths, protocol sizes, and pNFS layout sizing.

## Test Signals
Protocol serialization unit tests validate selected packet wrappers. Full compatibility depends on integration tests across mixed-version clients, masters, and chunkservers, plus Wireshark/tooling consumers if enabled.
