# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn321/dcn321_dio_link_encoder.h

## Purpose
This header declares the DCN321 link encoder constructor and inherits the DCN32 link encoder contract.

## Important APIs
The single public API is `dcn321_link_encoder_construct`, taking the standard `dcn20_link_encoder`, initialization data, feature support, link/AUX/HPD register tables, and shift/mask tables.

## Control Flow and State
No control flow is defined here. The constructor declared here initializes persistent link encoder object state and VBIOS-derived capability state in the C implementation.

## Dependencies and Integration Points
It includes `dcn32/dcn32_dio_link_encoder.h`, which supplies the reused DCN32 declarations and base register expectations.

## Risks and Test Signals
Risk is low but API signature drift would break DCN321 resource construction. Test signals are compile/link coverage for DCN321 resources and runtime validation that the expected DCN321 function table is installed.
