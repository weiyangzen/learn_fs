# sources/distributed-fs/ceph-client/drivers/media/tuners/fc001x-common.h

Purpose: common definitions shared by FC0012 and FC0013. It defines supported crystal frequencies (`FC_XTAL_27_MHZ`, `FC_XTAL_28_8_MHZ`, `FC_XTAL_36_MHZ`) and `FC_FE_CALLBACK_VHF_ENABLE` for parent frontend callbacks.

There is no state or control flow. The crystal enum drives PLL reference calculations in FC0012/FC0013, and the callback command lets parent demod/board code switch RF path or GPIO state for VHF.

Dependencies are only includers. Risks: enum value changes would silently alter persisted call-site ABI inside the kernel tree; callback semantics must remain aligned between tuner and parent frontend. Test signals: FC0012/FC0013 tuning across all crystal values and parent callback verification for frequencies below/above 300 MHz.
