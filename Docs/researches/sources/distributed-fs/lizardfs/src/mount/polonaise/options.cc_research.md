## sources/distributed-fs/lizardfs/src/mount/polonaise/options.cc

Purpose: parses command-line options for the Polonaise server and implements stream conversion for `SugidClearMode`.

Important APIs: `operator>>(std::istream&, SugidClearMode&)` accepts `never`, `always`, `osx`, `bsd`, `ext`, and `xfs`; `operator<<` prints the same tokens. `parse_command_line` fills a `Setup` struct with master host/port, bind port, mountpoint, password, IO retries, write buffer, cache settings, subfolder, daemonization, ACL flag, and Windows pipe name.

Control flow: Boost.Program_options defines options and defaults from `LizardClient::FsInitParams`. Parse errors print to stderr and `exit(1)`; `--help` prints usage and exits 0.

State and dependencies: writes only the passed `Setup`. Depends on Boost.Program_options and default mount client parameters.

Risks and tests: `enable-acl` is deprecated and ignored. `no-mkdir-copy-sgid` uses a bool switch whose default is the positive default value but later inverted in `main`; option semantics should be tested. Invalid sugid mode should throw validation errors.
