<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/bk_download.cpp -->
# sources/cloud-native/overlaybd/src/bk_download.cpp

Purpose: Implements delayed background download of remote layer blobs into local layer directories.

APIs and control flow: `check_downloaded` checks for `overlaybd.commit`. `BkDownload::download` short-circuits existing committed blobs, otherwise downloads into `.download`, verifies SHA256, renames to `overlaybd.commit`, and switches the active `ISwitchFile` to the local file. `download_blob` reads the source file in aligned blocks, optionally throttled, resumes sparse holes via `SEEK_HOLE`, and retries read/write failures. `bk_download_proc` delays startup, serializes per-dir locks, retries failed downloads, and exits when the owning image status changes.

State and persistence: Writes `.download` and `overlaybd.commit` under each layer dir; in-memory static `lock_files` guards duplicate downloads.

Dependencies and integration: Uses Photon localfs, throttled files, audit logging, `switch_file`, and `sha256file`.

Risks and test signals: `lock_files` is unsynchronized across threads. Sparse-file resume depends on filesystem `SEEK_HOLE`. Tests should corrupt `.download`, simulate retries, and verify switch-to-local behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/bk_download.cpp -->
