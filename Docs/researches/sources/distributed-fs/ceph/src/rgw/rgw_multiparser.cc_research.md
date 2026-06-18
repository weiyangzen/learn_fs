## sources/distributed-fs/ceph/src/rgw/rgw_multiparser.cc

Purpose: small standalone parser utility for multipart completion XML.

Important APIs/functions: `main()` initializes `RGWMultiXMLParser`, reads stdin in 1024-byte chunks, feeds chunks to `parser.parse(buf, len, done)`, reports parse failures, and exits.

Control flow: loop continues until EOF; each chunk indicates `done` based on `feof(stdin)`. Read errors exit with `-1`; parser initialization failure exits with `1`.

State and persistence: no persistent state. Parser object owns transient XML parse state.

Dependencies/integration: useful as a developer/test utility around `rgw_multi` XML parsing; depends on stdin and C stdio.

Risks and test signals: parse failures are printed but do not terminate the process immediately. Utility tests can feed valid/invalid multipart XML through stdin to exercise parser behavior outside the daemon.
