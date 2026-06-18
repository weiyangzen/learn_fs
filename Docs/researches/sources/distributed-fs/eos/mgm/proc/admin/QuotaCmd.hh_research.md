# sources/distributed-fs/eos/mgm/proc/admin/QuotaCmd.hh

## Purpose
`QuotaCmd.hh` declares the protobuf-backed quota command wrapper. It defines the command class and the private handler surface implemented in `QuotaCmd.cc`.

## Important APIs, Types, And Functions
`class QuotaCmd : public IProcCommand` accepts a `RequestProto` and `VirtualIdentity`, disables the parent constructor's third flag by passing `false`, and overrides `ProcessRequest() noexcept`. Private handlers cover `LsuserSubcmd`, `LsSubcmd`, `SetSubcmd`, `RmSubcmd`, and `RmnodeSubcmd`, each taking the matching generated `QuotaProto_*` message plus a reply reference.

## Control Flow
The header's structure makes `ProcessRequest()` the only public entry. The implementation switches on `QuotaProto::subcmd_case()` and delegates to one private method per protobuf oneof branch.

## State, Persistence, And Dependencies
The class has no additional data members. It depends on generated quota protobuf types, the command base class, and MGM namespace macros. Persistence is performed by implementation calls into quota services, not by the header itself.

## Integration Points
`QuotaCmd` plugs the console protobuf quota API into the MGM proc command execution framework. The method signatures are tightly coupled to `proto/Quota.pb.h`, so protobuf schema changes are compile-time visible here.

## Risks
The command surface is narrow but privileged. Because handlers are private, unit tests generally need to exercise them through `ProcessRequest()` or use friend-style harnesses. Handler signatures return through mutable reply objects, so omissions in implementation can leave default success-looking fields if not set consistently.

## Test Signals
Compile generated protobuf compatibility and dispatch every `QuotaProto` oneof case. Runtime checks should verify non-supported cases return `EINVAL`, and every handler sets `retc`, `std_out`, and `std_err` consistently.
