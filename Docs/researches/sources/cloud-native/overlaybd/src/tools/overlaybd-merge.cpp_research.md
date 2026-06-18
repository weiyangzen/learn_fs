# sources/cloud-native/overlaybd/src/tools/overlaybd-merge.cpp

Purpose: CLI that compacts multiple OverlayBD layers described by an image config into a single output layer, optionally zfile-compressed and uploaded.

Important APIs/types/functions: uses `create_overlaybd`, `ImageFile::compact`, `ZFile::new_zfile_builder`, `create_uploader`, and `registry_uploader_fini`. It defines a FIFO wrapper class, though the main path does not use it.

Control flow: parses service config, compression, tar, upload, credential/TLS, image config, and output path. It initializes Photon, creates an image file from config, opens the output, optionally wraps it in zfile and registry uploader, calls `compact(rst)`, closes output, finalizes registry upload, and prints the resulting digest.

State and persistence: writes a compacted layer file, may create a registry blob, and reads all lower layers referenced by the image config through image-service abstractions.

Dependencies/integration: bridges image-service layer stack resolution with zfile compression and registryfs uploading.

Risks: the tar option block wraps `rst` before `rst` is initialized, so `-t` with upload looks suspicious and likely ineffective or unsafe. Compression defaults to enabled through `run_callback_for_default`. Upload builder ownership and zfile builder ownership are implicit.

Test signals: needed cases include compact without compression, default compression, upload success/failure, missing image config, and the tar/upload option path.
