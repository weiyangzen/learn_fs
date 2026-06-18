# Research: sources/distributed-fs/eos/mgm/proc/admin/FileRegisterCmd.hh

## Purpose

`FileRegisterCmd.hh` declares the protobuf file-registration command handler for direct namespace metadata creation/update.

## Important APIs, Types, and Functions

- `FileRegisterCmd` derives from `IProcCommand`.
- The constructor moves `RequestProto` and stores caller identity.
- `ProcessRequest()` executes registration.

## Control Flow

`ProcInterface` constructs this handler for `RequestProto::kRecord`, an admin-only protobuf command. The implementation re-checks admin privileges before writing namespace metadata.

## State and Persistence Behavior

The header declares no extra state. All persistent effects happen in `FileRegisterCmd.cc` through namespace metadata operations.

## Dependencies and Integration Points

The header includes `proto/File.pb.h` and `ProcCommand.hh`, and is paired with `FileRegisterCmd.cc`.

## Risks and Edge Cases

- The command name is more specific than the included proto (`File.pb.h`), so proto schema changes can affect it indirectly.
- No private helper declarations exist; all implementation logic is concentrated in one method, making future extension harder to split cleanly.

## Test Signals

Compile coverage should ensure `FileRegisterProto` remains available through `File.pb.h`. Runtime tests should focus on the implementation's namespace mutation and admin checks.
