<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/bk_download.h -->
# sources/cloud-native/overlaybd/src/bk_download.h

Purpose: Public interface for background layer download.

APIs and types: Defines `BKDL::DOWNLOAD_TMP_NAME`, `check_downloaded`, class `BkDownload`, and `bk_download_proc`. `BkDownload` owns a source `IFile`, references an `ISwitchFile`, keeps file size, digest, URL, throttle, block size, retry count, target dir, and a reference to image running status.

State and persistence: The destructor unlocks the dir and deletes the source file. Downloaded state is represented by files on disk.

Dependencies and integration: `ImageFile::__open_ro_remote` creates `BkDownload` items when per-image download config is enabled.

Risks and test signals: Constructor takes `running` by reference, so lifetime must remain valid until thread completion; `ImageFile` destructor joins the thread to enforce this.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/bk_download.h -->
