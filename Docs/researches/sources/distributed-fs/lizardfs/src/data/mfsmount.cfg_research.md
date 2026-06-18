# sources/distributed-fs/lizardfs/src/data/mfsmount.cfg

Purpose: sample optional default options file for `mfsmount`.

Important syntax: options can be comma-separated on one line or split across lines; examples include `mfsmaster`, `mfsport`, `mfspassword`, and an absolute default mount point.

Control flow: client mount tooling reads the file to provide default mount parameters if present; all sample lines are commented.

State and persistence: persistent local client defaults; no runtime state.

Dependencies and integration: installed as a client example by the data CMake file.

Risks: storing passwords in the config may expose credentials through local file permissions. A default mount point must be absolute.

Test signals: no direct tests in this subset.
