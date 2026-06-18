<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/git/git.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/git/git.go

## Purpose

This IPLD plugin registers Git object codecs, including a compatibility decoder for zlib-compressed raw Git objects.

## Important APIs, Types, and Functions

`gitPlugin` implements `PluginIPLD`. `Register` registers a reserved-range decoder for zlib-encoded Git raw objects, plus standard GitRaw encoder and decoder. `decodeZlibGit` wraps the input with `zlib.NewReader` and delegates to `go-ipld-git.Decode`.

## Control Flow, State, and Integration

Loader injection mutates the global multicodec registry. Importing the go-ipld-git package also has codec registration side effects noted in the comment.

## Dependencies, Risks, and Test Signals

Dependencies are `compress/zlib`, go-ipld-git, go-ipld-prime, and multicodec IDs. Risks include registry conflicts, zlib reader errors, and reserved-range compatibility assumptions. Git DAG import/export tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/git/git.go -->
