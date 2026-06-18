# sources/distributed-fs/ceph-client/arch/arm/boot/dts/samsung/s3c64xx-pinctrl.h

Purpose: this header provides Samsung S3C64xx DTS pinctrl symbolic constants.

Important API surface: it defines pull modes `S3C64XX_PIN_PULL_NONE`, DOWN, and UP; and pin functions `INPUT`, `OUTPUT`, `FUNC_2` through `FUNC_6`, plus external interrupt function `S3C64XX_PIN_FUNC_EINT` with value 7.

Control flow: there is no executable logic. DTS preprocessing substitutes these names into pinctrl property cells.

State and persistence: no mutable state. Numeric constants persist in generated DTBs and are applied by the S3C64xx pinctrl driver.

Dependencies and integration: used by S3C64xx board DTS files such as mini6410 and smdk6410 builds. It follows Samsung pinctrl binding conventions but with the S3C64xx-specific EINT encoding.

Risks and test signals: a mismatch between function value and hardware register encoding breaks GPIO/peripheral muxing. Test S3C64xx DTB compilation and validate external interrupt and pull-up/down behavior on supported boards.
