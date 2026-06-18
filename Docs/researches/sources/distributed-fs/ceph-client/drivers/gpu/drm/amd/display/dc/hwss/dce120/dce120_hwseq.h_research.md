# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.h

Purpose: public header for the DCE12.0 hardware sequencer shim. It exposes the DCE120 constructor and the DCE12.1 xGMI state helper.

Important APIs, types, and functions: declares `bool dce121_xgmi_enabled(struct dce_hwseq *hws)` and `void dce120_hw_sequencer_construct(struct dc *dc)`. It includes core DC and private HW sequencer definitions and forward-declares `struct dc`.

Control flow: no executable flow exists. Including code can construct the DCE120 HWSS table or query xGMI state through the implementation.

State and persistence: no state is stored here. The function prototypes expose `dc` and `dce_hwseq`, which give the implementation access to register helpers and HWSS function-table mutation.

Dependencies and integration points: used by DCE12 resource construction and code paths that need xGMI awareness. It depends on the DCE private HW sequencer type for the xGMI helper signature.

Risks and test signals: build risk comes from the xGMI helper requiring `struct dce_hwseq` visibility via included headers. The include guard comment names DCE112, which is cosmetic but can confuse maintenance. Test signals are successful DCE120 builds and constructor selection on DCE12 hardware.
