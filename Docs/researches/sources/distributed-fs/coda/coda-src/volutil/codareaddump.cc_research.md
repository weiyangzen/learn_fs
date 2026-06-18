## sources/distributed-fs/coda/coda-src/volutil/codareaddump.cc

Purpose: `codareaddump.cc` is an interactive dump-inspection utility. It provides parser commands to open a Coda dump, show the dump header and volume disk data, select large or small vnode indexes, skip vnodes, and print vnode disk objects.

Important APIs/types/functions: the command table exposes `openDumpFile`, `setIndex`, `showHeader`, `showVolumeDiskData`, `nextVnode`, `skipVnodes`, and `quit`. Global state includes `DefaultDumpFile`, `DefaultSize`, `DumpStream`, and `Open`. Helper functions include `Rewind`, `PrintVersionVector`, `showHeader`, `showVolumeDiskData`, `setIndex`, `skipVnodes`, and `showVnodeDiskObject`.

Control flow: `main` seeds the default dump filename if provided, initializes the parser prompt, and hands control to `Parser_commands`. Most commands verify a dump is open, often rewind by destroying/recreating `dumpstream`, then call stream APIs. `setIndex` reads the header and volume metadata, reads the large index, and optionally scans all large vnodes before reading the small index. `showVnodeDiskObject` and `skipVnodes` advance from the current stream position.

State and persistence behavior: this tool is read-only with respect to dumps and Coda state. It keeps only interactive process state: current dumpstream position, default filename, and default vnode class. Rewind requires a named file; stdin/empty filename cannot be reliably rewound or seeked.

Dependencies/integration points: uses Coda parser library, `dumpstream`, `DumpHeader`, `VolumeDiskData`, `VnodeDiskObject`, version vector printing, and vnode numbering conventions. It is mainly a diagnostic companion to `vol-dump`, restore code, `codamergedump`, and `codadump2tar`.

Risks: commands assume a correct stream position; using `nextVnode` before `setIndex` or after payload data can misparse. `strncpy` into local buffers may not always null-terminate if the input exactly fills the buffer. Many errors are printed but do not reset state. It prints raw pointer-like inode/dir node fields that are meaningful only inside Coda internals. It does not display external ACL payloads.

Test signals: open full and incremental dumps, verify header/volume fields match `vol-dump`, step through both vnode classes, skip past directory/file payloads, and test behavior on invalid/truncated dumps. Interactive regression tests can feed command scripts to stdin and compare stable portions of output.
