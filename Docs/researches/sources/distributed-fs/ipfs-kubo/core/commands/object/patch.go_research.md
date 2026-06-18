# sources/distributed-fs/ipfs-kubo/core/commands/object/patch.go

## Purpose

`object/patch.go` implements the remaining deprecated `ipfs object patch` subcommands for adding and removing links in dag-pb objects. It is retained for legacy workflows but warns users to prefer MFS `files` commands.

## Important APIs, Types, and Functions

`ObjectPatchCmd` exposes deprecated `add-link` and `rm-link`, while removed patch operations route to `RemovedObjectCmd`. `patchRmLinkCmd` uses `api.Object().RmLink`; `patchAddLinkCmd` uses `api.Object().AddLink`. Options include `--create`, `--allow-non-unixfs`, and the shared big-block allowance check. Both emit `Object{Hash: <cid>}`.

## Control Flow

`rm-link` parses the root path/CID, target link name, and UnixFS-validation bypass flag, then calls CoreAPI to create a new object without that link. `add-link` parses root, link name, and child ref, handles `--create` for intermediary nodes, and calls CoreAPI to create a new object with the link. Both commands get the request CID encoder, check resulting CID size via `cmdutils.CheckCIDSize`, and text-encode the new root hash.

## State and Persistence Behavior

The commands do not mutate existing immutable objects. They persist newly created DAG blocks through CoreAPI object patch operations. They may create invalid UnixFS structures if validation is bypassed or if used on sharded directories/files.

## Dependencies and Integration Points

Dependencies include Kubo CoreAPI object methods, command path utilities, CID-size enforcement, and command encoders. The file integrates with the deprecated `object` command tree and indirectly with MFS migration guidance in help text.

## Risks and Test Signals

Risks include producing malformed UnixFS, bypassing validation, big-block/CID-size policy violations, and confusion between immutable object creation and filesystem mutation. Tests should cover add/remove success, missing roots/children, invalid path inputs, `--create`, `--allow-non-unixfs`, CID-size rejection, deprecated status, and text/JSON output.
