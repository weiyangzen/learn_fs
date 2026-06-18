# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_ftp.h

## Purpose
Defines FTP conntrack helper message types exposed to userspace.

## Important APIs, Types, And Functions
Exports `nf_ct_ftp_type` values for FTP `PORT`, `PASV`, `EPRT`, and `EPSV`.

## Control Flow
The FTP helper parses control-channel commands/replies and classifies expectations by these types for userspace visibility or helper logic.

## State, Persistence, And Dependencies
State persists in FTP-related conntrack expectations and helper metadata. No external dependencies.

## Integration Points
Used by conntrack helpers and ctnetlink users decoding FTP expectation type.

## Risks
Only type identifiers are defined; parsing and security validation happen elsewhere. FTP control parsing is sensitive to NAT and malformed commands.

## Test Signals
Validate helper classification for active/passive IPv4 and extended IPv6-aware FTP commands, and ctnetlink reporting of expectation types.
