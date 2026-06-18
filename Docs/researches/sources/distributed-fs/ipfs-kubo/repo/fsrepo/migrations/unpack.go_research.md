# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/unpack.go

Purpose: extracts a named binary from downloaded migration archives.

Important APIs and control flow: `unpackArchive` dispatches on `tar.gz` or `zip`. `unpackTgz` opens gzip/tar, scans entries for `<root>/<name>`, and writes the matched stream. `unpackZip` scans zip entries for the same path and writes the opened file. `writeToPath` creates the output file and copies bytes.

State and persistence: reads archive files and writes extracted binaries. It does not sanitize arbitrary archive paths beyond exact match to expected root/name.

Dependencies and integration: used by `FetchBinary`; test helpers also create matching archives.

Risks and test signals: output creation is not atomic and can leave partial files on copy error. Zip file readers are not explicitly closed for the selected entry after `writeToPath`, though archive close handles resources. Tests cover bad archive types, corrupt archives, missing binary, and successful tar/zip extraction.
