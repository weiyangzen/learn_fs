## sources/cloud-native/overlaybd/src/switch_file.cpp

Purpose: implements a delegating `IFile` that initially reads from a source file and can switch to a local downloaded file, optionally treating local/remote data as tar and/or zfile. It is used to move reads from remote/cache paths to local committed data after background download.

Important types/functions: `try_open_zfile` checks `ZFile::is_zfile` and wraps zfiles with `zfile_open_ro`. `SwitchFile` implements `ISwitchFile` and forwards most `IFile` operations to `m_local_file` when present, otherwise `m_file`. `set_switch_file` opens a local path, wraps it as tar, then zfile if applicable, and installs it as the local target. `new_switch_file` detects zfile on the initial source and retries once.

Control flow: initial construction stores either source as local or remote. Forwarding uses the `FORWARD` macro. `pread` adds an audit threshold when serving local reads. Switching opens the local file, adapts to tar, tries zfile detection/open, and only updates `m_local_file` on success.

State/persistence: in-memory pointers to current remote and local files plus path string; destructor deletes both. Persistent state is the local file path supplied to `set_switch_file`. Dependencies are Photon filesystem/localfs, audit logging, tar adaptor, and zfile APIs.

Integration points: bridges downloaded commit files and zfile/tar formats into the image read path. Risks: no synchronization protects switching while other threads read; failed `try_open_zfile` after tar wrapping may delete only the current pointer path and needs careful ownership reasoning; forwarding writes to local when present even though local switched data may be read-only depending on adaptor. Test coverage is indirect through zfile and image service paths, not a dedicated switch-file test in this subset.
