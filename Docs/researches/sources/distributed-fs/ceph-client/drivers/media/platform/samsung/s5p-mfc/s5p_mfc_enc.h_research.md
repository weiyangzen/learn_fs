# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_enc.h

Purpose: declares the public encoder-side hooks exported by `s5p_mfc_enc.c` to the S5P MFC core.

Important APIs and types: exposes accessor functions for `struct s5p_mfc_codec_ops`, `struct vb2_ops`, and `struct v4l2_ioctl_ops`, plus encoder control lifecycle helpers `s5p_mfc_enc_ctrls_setup` and `s5p_mfc_enc_ctrls_delete`, and default-format initializer `s5p_mfc_enc_init`.

Control flow: the core MFC probe/open path includes this header, initializes a context with `s5p_mfc_enc_init`, installs V4L2 controls through `s5p_mfc_enc_ctrls_setup`, and binds the returned ioctl/vb2/codec operation tables to the encoder video device and context.

State and persistence: no state is stored in the header. All functions operate on caller-owned `struct s5p_mfc_ctx` or return static operation tables owned by the implementation.

Dependencies and integration points: relies on consumers already knowing `struct s5p_mfc_ctx`, `struct s5p_mfc_codec_ops`, `struct vb2_ops`, and `struct v4l2_ioctl_ops` through MFC and media headers. It is the narrow integration boundary between generic MFC context setup and the encoder implementation.

Risks: the header does not include or forward-declare the referenced structures, so include ordering must provide type declarations. ABI expectations are internal to the kernel driver but mismatched table lifetimes or missing setup/cleanup calls would leak controls.

Test signals: compile coverage of MFC encoder registration and context open/close paths; control handler leak checks on repeated open/close; and link coverage proving the exported functions are present.
