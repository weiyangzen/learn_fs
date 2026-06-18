<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/qcom_adm.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/qcom_adm.h

## Purpose
Defines Qualcomm ADM DMA peripheral configuration.

## Important APIs, Types, And Functions
`struct qcom_adm_peripheral_config` contains `crci` and `mux` fields used to select peripheral request and mux routing.

## Control Flow
Peripheral drivers pass the config to the ADM DMA driver when requesting or configuring a DMA channel. The DMA driver programs CRCI and mux settings for the hardware path.

## State And Persistence
State is channel routing configuration. No persistence exists.

## Dependencies And Integration Points
Depends on Qualcomm ADM DMA controller semantics and peripheral request routing.

## Risks And Edge Cases
Incorrect CRCI or mux values route DMA requests incorrectly or prevent transfers. The structure has no validation by itself.

## Test Signals
Tests should cover representative peripherals, valid/invalid CRCI values, mux selection, and transfer completion after channel setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/qcom_adm.h -->
