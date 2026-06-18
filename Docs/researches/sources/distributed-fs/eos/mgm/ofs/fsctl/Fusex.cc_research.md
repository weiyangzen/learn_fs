<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Fusex.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Fusex.cc

Source read size: 84 lines, 3432 bytes.

## Purpose

Implements the write-side eosxd/FUSE protocol fsctl entry point `XrdMgmOfs::Fusex`. It accepts a serialized `eos::fusex::md` protobuf request, dispatches it to the in-process FuseX server, and returns a base64-encoded protobuf response.

## Important APIs, Types, and Functions

The main API is `XrdMgmOfs::Fusex(...)`. It parses `eos::fusex::md`, derives `vid.app` from `gOFS->zMQ->gFuseServer.Client().client2app(md.clientid())`, records `Eosxd::prot::SET` stats, and calls `gFuseServer.HandleMD(id, md, vid, &resultstream, 0)`.

## Control Flow

The handler enters write mode, allows master redirection, starts timing, parses the protobuf string, maps the client id to an app name, applies stall handling, and invokes the FuseX metadata server with a synchronous id based on `vid.tident`. Nonparseable input, handler errors, and empty responses become `Emsg`; successful responses are base64 encoded and returned as `Fusex:<encoded>`.

## State and Persistence Behavior

This file owns no state. Persistent namespace/cache changes are performed inside the FuseX server. It mutates the request identity's app field for accounting and downstream authorization/audit.

## Dependencies and Integration Points

Depends on `mgm/zmq/ZMQ.hh`, FuseX protobuf definitions, `XrdMgmOfs`, access/redirect/stall macros, `MgmStats`, and `SymKey::Base64`. It is the fsctl bridge from eosxd clients into `gFuseServer.HandleMD`.

## Risks and Edge Cases

Large protobufs are only logged by length; malformed input is rejected early. Empty FuseX responses are treated as illegal even if the handler returned success. The app is trusted from client id mapping, so stale FuseX client registration affects accounting. Error text is generic (`handle request`) and may hide detailed handler diagnostics.

## Test Signals

Cover parse failure, valid metadata mutation returning nonempty output, empty handler response, handler nonzero rc, app mapping from client id, redirect/stall behavior on followers, and base64 round-trip of the result stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Fusex.cc -->
