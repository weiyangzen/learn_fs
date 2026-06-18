# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.h

Purpose: Declares the DCN10 link encoder register model, common field lists reused by newer DCN generations, and the public link-encoder API implemented in `dcn10_link_encoder.c`.

Important APIs/types/functions: Register structs cover link, AUX, and HPD blocks. Macro field lists span DIG enable/mode/source, DP DPHY, MST SAT, AUX, HPD, and many DCN20+ DPCS/UNIPHY fields used by derived encoders. `struct dcn10_link_encoder` embeds `struct link_encoder` and stores register metadata. Prototypes expose construction, validation, init, setup, enable/disable, lane training, MST allocation, PSR, AUX, HPD, capability, and readback helpers.

Control flow: None in the header; it defines the static interface and macro expansion surface used by resource tables.

State/persistence: The C object stores base link encoder state and immutable register metadata pointers. HPD GPIO lifetime is owned through the base and destroyed by the C implementation.

Dependencies/integration: Includes `link_encoder.h` and is included by DCN20 link encoder headers for inheritance/reuse.

Risks: This header is a shared compatibility point for multiple generations, so adding/removing fields can affect DCN20, DCN30, DCN31, and DCN35 users. Some prototypes such as RGB/wireless validation are declared here but not implemented in the reviewed C file, so users must not assume every declaration is locally defined.

Test signals: Compile/link coverage across all DIO generations using the shared field lists, plus resource-table initialization tests for AUX/HPD/link register mappings.
