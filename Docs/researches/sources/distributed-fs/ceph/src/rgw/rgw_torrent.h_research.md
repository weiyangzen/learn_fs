# sources/distributed-fs/ceph/src/rgw/rgw_torrent.h

## Purpose
`rgw_torrent.h` declares bencode helpers, torrent read support, and the put-object pipeline filter that computes torrent metadata.

## Important APIs, Types, and Functions
Free functions write bencode control characters, keys, values, and dictionary entries. `rgw_read_torrent_file()` reads a complete torrent file for an object. `RGWPutObj_Torrent` derives from `rgw::putobj::Pipe`, overrides `process()`, and exposes `bencode_torrent(filename)`.

## Control Flow
Callers insert `RGWPutObj_Torrent` into the upload data processor chain, stream object data through it, then request the final bencoded torrent metadata after completion.

## State and Persistence Behavior
The class holds only upload-local hash state and does not persist on its own.

## Dependencies and Integration Points
Depends on `rgw_putobj.h`, SAL forward declarations, Ceph SHA1, async yield context, and Dout logging. It integrates with object upload and GetObjectTorrent paths.

## Risks
The class assumes a final zero-length flush call to capture partial-piece hashes. If callers skip it, torrent metadata will miss the last piece.

## Test Signals
Pipeline tests should confirm downstream forwarding, final flush behavior, disabled output above max length, and correct piece hash count.
