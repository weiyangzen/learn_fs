# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-gen.h

Purpose: defines the VBI generator state structure and declares raw/sliced VBI generation APIs.

Important APIs and types: `struct vivid_vbi_gen_data` contains 25 sliced VBI records and a 16-byte time-of-day packet cache. `vivid_vbi_gen_sliced` fills sliced records for a standard and sequence number; `vivid_vbi_gen_raw` renders those records into a raw VBI buffer using a `v4l2_vbi_format`.

Control flow: VBI capture first calls sliced generation, optionally adjusts records for loopback/aspect, then calls raw generation for raw VBI buffers.

State and persistence: the structure persists generated records across processing steps within a capture tick.

Dependencies and integration points: consumers need V4L2 sliced/raw VBI types.

Risks: the fixed 25-record array reflects current generated services; adding more service lines requires resizing the structure and dependent loops.

Test signals: generated sliced record count and raw conversion tests validate this header contract.
