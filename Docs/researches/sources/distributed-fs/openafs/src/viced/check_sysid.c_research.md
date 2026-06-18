# sources/distributed-fs/openafs/src/viced/check_sysid.c

Purpose: implements a small diagnostic command, `check_sysid`, that reads an OpenAFS fileserver sysid file and prints its version stamp, server UUID, and recorded IP addresses. It is meant for verification and inspection, not for modifying state.

Important APIs/functions: `main` is the only function. It validates the command line (`check_sysid <sysid_file>`), opens the file read-only, reads a local `struct versionStamp`, reads an `opr_uuid_t`, converts the UUID with `opr_uuid_toString`, reads an address count, then reads and prints each IPv4 address after `ntohl`. Constants `SYSIDMAGIC` and `SYSIDVERSION` define the expected file stamp.

Control flow: errors are handled immediately with printed diagnostics and distinct exits for open failure, UUID read failure, entry count read failure, address read failure, and UUID formatting failure. Magic/version mismatches are reported inline but do not abort parsing. The tool trusts the `nentries` value enough to iterate that many times and stops only on short reads.

State and persistence behavior: no persistent state is written. The file format fields are interpreted exactly as documented in comments: magic/version and number-of-addresses are in host byte order, UUID contains network-order portions as defined by UUID layout, and each address is stored in network byte order. The only dynamic allocation is the UUID string buffer returned by `opr_uuid_toString`, freed with `opr_uuid_freeString`.

Dependencies and integration: includes OpenAFS config/param headers, roken portability wrappers, VLDB integer types, and `opr/uuid.h`. The sysid format mirrors fileserver/volume-server identity state used elsewhere in OpenAFS server startup and registration code. The source contains a local copy of `struct versionStamp` noted as stolen from `afs/volume.h`, which keeps the utility lightweight but couples it to that layout.

Risks: the tool does not validate negative or huge `nentries`, so a corrupt file can cause long reads/printing until EOF. The magic mismatch message says `(should be 0x88aabbc)`, missing one `c` compared with `SYSIDMAGIC` `0x88aabbcc`. It uses `int` for addresses and sizes, which is adequate for the legacy format but not a general binary parser pattern. Host byte order fields mean sysid files are not portable across endian architectures without special handling.

Test signals: create fixture sysid files with valid stamp/UUID/address lists, truncated version/UUID/count/address sections, wrong magic/version, zero addresses, and multiple addresses. Verify exit status and printed dotted-quad output. Static-analysis signals include unchecked continuation after a short version-stamp read and unbounded `nentries`.
