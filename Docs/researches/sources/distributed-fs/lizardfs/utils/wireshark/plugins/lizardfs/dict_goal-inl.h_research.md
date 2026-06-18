# sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/dict_goal-inl.h

Purpose: value-string include fragment for LizardFS goal codes in Wireshark.

Important data: maps replication goals 1 through 9 to `goal1`..`goal9`, and XOR goals 255 down to 247 to `xor2`..`xor10`.

Control flow/state: data-only initializer fragment without guards. It is consumed inside generated C arrays.

Dependencies/integration: included by `make_dissector.py` generated code for `goal` fields, which are listed as externally-dictionaried fields.

Risks and test signals: risks are protocol drift if goal encodings change or new storage classes are added. Test signals are packet dissection for file attributes or set-goal messages containing normal and XOR goal values.
